import requests
import time
import json
import re
from typing import Optional
from config import API_KEY, API_BASE_URL, API_MODEL, API_TIMEOUT, API_MAX_RETRIES


def _get_system_api_key() -> Optional[str]:
    """Read the admin-configured system-wide API key from SystemConfig table (encrypted)."""
    try:
        from database import SessionLocal
        from models import SystemConfig
        from utils.encryption import decrypt
        db = SessionLocal()
        try:
            cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_key").first()
            if cfg and cfg.value:
                return decrypt(cfg.value)
            return None
        finally:
            db.close()
    except Exception:
        return None


def _get_system_api_model() -> Optional[str]:
    try:
        from database import SessionLocal
        from models import SystemConfig
        db = SessionLocal()
        try:
            cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_model").first()
            return cfg.value if cfg else None
        finally:
            db.close()
    except Exception:
        return None


def _get_system_api_base_url() -> Optional[str]:
    try:
        from database import SessionLocal
        from models import SystemConfig
        db = SessionLocal()
        try:
            cfg = db.query(SystemConfig).filter(SystemConfig.key == "system_api_base_url").first()
            return cfg.value if cfg else None
        finally:
            db.close()
    except Exception:
        return None


class APIError(Exception):
    pass


class ValidationError(Exception):
    pass


def extract_json(text: str) -> str:
    """Extract JSON from LLM response that may be wrapped in markdown code blocks.
    Handles nested code fences (e.g. Python code examples inside JSON string values)."""
    # Find outermost ```json ... ``` block by locating the LAST closing ```
    start_match = re.search(r"```(?:json)?\s*\n", text)
    if start_match:
        content_start = start_match.end()
        # Find the LAST ``` in the text (the outermost closing fence)
        last_fence = text.rfind("```")
        if last_fence > content_start:
            return text[content_start:last_fence].strip()
    # Try to find a JSON object directly (greedy)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0).strip()
    return text.strip()


def repair_json(text: str) -> str:
    """Fix common LLM JSON issues: unescaped newlines in strings, trailing commas."""
    # Remove literal newlines inside JSON strings (replace with \\n)
    # This is a heuristic: find strings and escape internal newlines
    result = []
    in_string = False
    escape_next = False
    for ch in text:
        if escape_next:
            result.append(ch)
            escape_next = False
            continue
        if ch == '\\':
            result.append(ch)
            escape_next = True
            continue
        if ch == '"' and not escape_next:
            in_string = not in_string
            result.append(ch)
            continue
        if in_string and ch == '\n':
            result.append('\\n')
            continue
        if in_string and ch == '\r':
            result.append('\\r')
            continue
        if in_string and ch == '\t':
            result.append('\\t')
            continue
        result.append(ch)
    return ''.join(result)


def safe_json_parse(text: str) -> dict:
    """Parse JSON from LLM response, handling markdown wrapping and common issues."""
    extracted = extract_json(text)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError:
        # Try repairing common issues
        repaired = repair_json(extracted)
        return json.loads(repaired)


def validate_api_key(api_key: str) -> bool:
    if not api_key:
        return False
    if api_key == "your_api_key_here":
        return False
    return True


def validate_prompt(prompt: str) -> bool:
    if not prompt or not isinstance(prompt, str):
        return False
    if len(prompt.strip()) == 0:
        return False
    return True


def call_qwen_api(
    prompt: str,
    api_key: Optional[str] = None,
    api_model: Optional[str] = None,
    api_base_url: Optional[str] = None,
) -> str:
    key = api_key or _get_system_api_key() or API_KEY
    model = api_model or _get_system_api_model() or API_MODEL
    base_url = api_base_url or _get_system_api_base_url() or API_BASE_URL

    if not validate_api_key(key):
        raise ValidationError("API密钥无效，请检查API Key配置")

    if not validate_prompt(prompt):
        raise ValidationError("Prompt内容不能为空")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=API_TIMEOUT
        )

        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            raise APIError("API认证失败，请检查API密钥是否正确")
        elif response.status_code == 403:
            raise APIError("API访问被拒绝，请确认API密钥有权限访问该服务")
        elif response.status_code == 429:
            raise APIError("API请求频率超限，请稍后重试")
        elif response.status_code >= 500:
            raise APIError(f"服务内部错误: {response.status_code}")
        else:
            raise APIError(f"API调用失败: {response.status_code}, {response.text}")

    except requests.exceptions.Timeout:
        raise APIError(f"API请求超时（{API_TIMEOUT}秒），请检查网络连接后重试")
    except requests.exceptions.ConnectionError:
        raise APIError("网络连接失败，请检查网络设置后重试")
    except requests.exceptions.RequestException as e:
        raise APIError(f"请求异常: {str(e)}")


def call_qwen_api_with_retry(
    prompt: str,
    api_key: Optional[str] = None,
    api_model: Optional[str] = None,
    api_base_url: Optional[str] = None,
    max_retries: Optional[int] = None,
    user_id: Optional[int] = None,
    endpoint: str = "",
) -> str:
    retries = max_retries or API_MAX_RETRIES
    model = api_model or API_MODEL
    start_time = time.time()

    for attempt in range(retries):
        try:
            result = call_qwen_api(
                prompt,
                api_key=api_key,
                api_model=api_model,
                api_base_url=api_base_url,
            )
            # Log success
            latency_ms = int((time.time() - start_time) * 1000)
            try:
                from services.admin_service import log_api_call
                # Estimate tokens (rough: ~4 chars per token for Chinese)
                estimated_prompt_tokens = len(prompt) // 2
                estimated_completion_tokens = len(result) // 2
                log_api_call(
                    user_id=user_id,
                    endpoint=endpoint,
                    model=model,
                    prompt_tokens=estimated_prompt_tokens,
                    completion_tokens=estimated_completion_tokens,
                    latency_ms=latency_ms,
                    status="success",
                )
            except Exception:
                pass  # never let logging break the main flow
            return result
        except (APIError, ValidationError) as e:
            is_auth_error = "认证失败" in str(e) or "访问被拒绝" in str(e)
            if attempt == retries - 1 or is_auth_error:
                # Log failure
                latency_ms = int((time.time() - start_time) * 1000)
                try:
                    from services.admin_service import log_api_call
                    log_api_call(
                        user_id=user_id,
                        endpoint=endpoint,
                        model=model,
                        latency_ms=latency_ms,
                        status="error",
                        error_message=str(e)[:500],
                    )
                except Exception:
                    pass
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)

    raise APIError("API调用失败，已达到最大重试次数")


def test_api_connection(
    api_key: Optional[str] = None,
    api_model: Optional[str] = None,
    api_base_url: Optional[str] = None,
) -> dict:
    key = api_key or _get_system_api_key() or API_KEY
    model = api_model or _get_system_api_model() or API_MODEL
    base_url = api_base_url or _get_system_api_base_url() or API_BASE_URL

    test_prompt = "你好，请回复OK"

    try:
        result = call_qwen_api(test_prompt, api_key=key, api_model=model, api_base_url=base_url)
        return {
            "success": True,
            "message": "API连接测试成功",
            "response": result
        }
    except ValidationError as e:
        return {
            "success": False,
            "message": f"配置验证失败: {str(e)}",
            "response": None
        }
    except APIError as e:
        return {
            "success": False,
            "message": f"API调用失败: {str(e)}",
            "response": None
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"未知错误: {str(e)}",
            "response": None
        }