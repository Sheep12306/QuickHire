import os
from pathlib import Path
from dotenv import load_dotenv, set_key
import requests

ENV_FILE = Path(__file__).parent / ".env"


def load_api_config() -> dict:
    load_dotenv(ENV_FILE, override=True)
    return {
        "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
        "base_url": os.getenv("API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"),
        "model": os.getenv("API_MODEL", "qwen-plus"),
        "timeout": os.getenv("API_TIMEOUT", "30"),
        "max_retries": os.getenv("API_MAX_RETRIES", "3"),
    }


def save_api_config(api_key: str, base_url: str = None, model: str = None,
                    timeout: str = None, max_retries: str = None) -> bool:
    os.makedirs(ENV_FILE.parent, exist_ok=True)
    if not ENV_FILE.exists():
        ENV_FILE.touch()

    set_key(str(ENV_FILE), "DASHSCOPE_API_KEY", api_key)
    if base_url:
        set_key(str(ENV_FILE), "API_BASE_URL", base_url)
    if model:
        set_key(str(ENV_FILE), "API_MODEL", model)
    if timeout:
        set_key(str(ENV_FILE), "API_TIMEOUT", timeout)
    if max_retries:
        set_key(str(ENV_FILE), "API_MAX_RETRIES", max_retries)

    # Reload env vars into os.environ
    load_dotenv(ENV_FILE, override=True)
    return True


def is_api_configured() -> bool:
    config = load_api_config()
    key = config["api_key"]
    if not key or key == "your-api-key-here" or key == "your_api_key_here":
        return False
    return True


def test_api_connection(api_key: str = None, base_url: str = None) -> dict:
    key = api_key or load_api_config()["api_key"]
    url = base_url or load_api_config()["base_url"]

    if not key or key == "your-api-key-here":
        return {"success": False, "message": "请先配置有效的 API Key"}

    try:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
            },
            json={
                "model": load_api_config()["model"],
                "messages": [{"role": "user", "content": "回复OK"}],
            },
            timeout=10,
        )
        if response.status_code == 200:
            return {"success": True, "message": "API 连接正常"}
        elif response.status_code == 401:
            return {"success": False, "message": "API Key 无效，请检查后重试"}
        elif response.status_code == 403:
            return {"success": False, "message": "API 访问被拒绝，请确认权限"}
        else:
            return {"success": False, "message": f"API 返回错误: {response.status_code}"}
    except requests.exceptions.Timeout:
        return {"success": False, "message": "连接超时，请检查网络"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "message": "网络连接失败"}
    except Exception as e:
        return {"success": False, "message": f"未知错误: {str(e)}"}
