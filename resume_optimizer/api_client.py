import requests
import time
from typing import Optional
from config import API_KEY, API_BASE_URL, API_MODEL, API_TIMEOUT, API_MAX_RETRIES


class APIError(Exception):
    pass


class ValidationError(Exception):
    pass


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


def call_qwen_api(prompt: str, api_key: Optional[str] = None) -> str:
    key = api_key or API_KEY

    if not validate_api_key(key):
        raise ValidationError("API密钥无效，请检查.env文件中的DASHSCOPE_API_KEY配置")

    if not validate_prompt(prompt):
        raise ValidationError("Prompt内容不能为空")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": API_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(
            API_BASE_URL,
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
            raise APIError(f"通义千问服务内部错误: {response.status_code}")
        else:
            raise APIError(f"API调用失败: {response.status_code}, {response.text}")

    except requests.exceptions.Timeout:
        raise APIError(f"API请求超时（{API_TIMEOUT}秒），请检查网络连接后重试")
    except requests.exceptions.ConnectionError:
        raise APIError("网络连接失败，请检查网络设置后重试")
    except requests.exceptions.RequestException as e:
        raise APIError(f"请求异常: {str(e)}")


def call_qwen_api_with_retry(prompt: str, api_key: Optional[str] = None, max_retries: Optional[int] = None) -> str:
    retries = max_retries or API_MAX_RETRIES

    for attempt in range(retries):
        try:
            return call_qwen_api(prompt, api_key)
        except APIError as e:
            if attempt == retries - 1:
                raise
            if "认证失败" in str(e) or "访问被拒绝" in str(e):
                raise
            wait_time = 2 ** attempt
            time.sleep(wait_time)

    raise APIError("API调用失败，已达到最大重试次数")


def test_api_connection(api_key: Optional[str] = None) -> dict:
    key = api_key or API_KEY

    test_prompt = "你好，请回复OK"

    try:
        result = call_qwen_api(test_prompt, key)
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