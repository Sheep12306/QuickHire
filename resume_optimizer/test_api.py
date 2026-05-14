import sys
sys.path.insert(0, '.')

from api_client import test_api_connection, API_KEY

print("=" * 50)
print("API连接测试")
print("=" * 50)

print(f"\nAPI密钥状态: {'已配置' if API_KEY and API_KEY != 'your_api_key_here' else '未配置'}")
if API_KEY:
    print(f"密钥前缀: {API_KEY[:10]}...")

result = test_api_connection()

print(f"\n测试结果: {'✅ 成功' if result['success'] else '❌ 失败'}")
print(f"消息: {result['message']}")

if result['response']:
    print(f"API响应: {result['response'][:100]}...")

print("=" * 50)