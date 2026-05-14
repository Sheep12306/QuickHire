# AI简历优化&面试题生成系统

基于Python+Streamlit+通义千问大模型的智能简历优化与个性化面试题生成系统。

## 功能特性

- **📄 简历智能优化**：AI一键润色，突出亮点，量化成果
- **📚 个性化面试题生成**：基于简历内容生成专属面试题，千人千题
- **🔄 优化对比展示**：双栏对比，优化效果一目了然
- **💾 多格式导出**：支持复制、下载功能

## 项目结构

```
resume_optimizer/
├── app.py              # 主程序
├── config.py            # 系统配置
├── api_client.py        # API调用模块
├── resume_parser.py     # 简历解析模块
├── prompt_builder.py    # Prompt构造模块
├── .env                 # 环境变量配置
├── requirements.txt     # 依赖清单
└── README.md            # 项目说明
```

## 环境要求

- Python 3.8+
- 通义千问API密钥

## 详细安装配置步骤

### 第一步：安装Python依赖

打开终端，进入项目目录，执行以下命令：

```bash
cd resume_optimizer
pip install -r requirements.txt
```

**依赖说明**：
| 依赖包 | 版本 | 说明 |
|--------|------|------|
| streamlit | ≥1.28.0 | Web应用框架 |
| python-dotenv | ≥1.0.0 | 环境变量管理 |
| requests | ≥2.31.0 | HTTP请求库 |

### 第二步：获取通义千问API密钥

#### 2.1 注册阿里云账号

1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 点击"立即注册"或"登录"
3. 可使用淘宝账号/支付宝账号快速登录

#### 2.2 申请API密钥

1. 登录后进入控制台
2. 选择「模型服务」→「API-KEY管理」
3. 点击「创建API-KEY」
4. 复制生成的密钥（格式：`sk-xxxxxxxxxxxxxxxx`）

#### 2.3 填写API密钥

打开项目目录中的 `.env` 文件：

```env
# 通义千问API密钥
DASHSCOPE_API_KEY=sk-your-actual-api-key-here

# API配置（一般不需要修改）
API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
API_MODEL=qwen-plus
API_TIMEOUT=30
API_MAX_RETRIES=3
```

**⚠️ 重要提示**：
- 将 `sk-your-actual-api-key-here` 替换为您的实际API密钥
- 不要泄露您的API密钥给他人
- API密钥相当于您的账号密码

### 第三步：验证API配置

启动应用程序：

```bash
streamlit run app.py
```

浏览器会自动打开页面。如果API密钥配置正确：

1. 在左侧边栏找到「🔑 API状态」
2. 点击「🔄 测试API连接」按钮
3. 看到绿色"✅ API连接成功"即表示配置正确

**常见API错误及解决方法**：

| 错误信息 | 原因 | 解决方法 |
|---------|------|---------|
| API密钥无效 | 密钥格式错误或为空 | 检查.env文件中API_KEY是否正确 |
| API认证失败 | API密钥不正确 | 确认API密钥与阿里云控制台一致 |
| API访问被拒绝 | 账号余额不足 | 充值阿里云账户 |
| 请求频率超限 | 调用过于频繁 | 等待后重试，或联系客服提高限额 |

### 第四步：启动应用

```bash
streamlit run app.py
```

应用启动后，访问 `http://localhost:8501`

## 使用说明

### 简历优化模式

1. 在左侧选择「📄 简历优化」模式
2. 输入或粘贴简历内容
3. 设置目标岗位（如：Python开发工程师）
4. 选择优化风格（简洁专业/突出业绩/技术导向/创新风格）
5. 点击「🚀 开始优化简历」
6. 查看优化前后对比结果
7. 复制或下载优化后的简历

### 面试题生成模式

1. 在左侧选择「📚 面试题生成」模式
2. 输入或粘贴简历内容
3. 配置参数：
   - **难度级别**：入门/基础/中等/面试高频/深度深挖
   - **题目类型**：选择题/简答题/项目手撕题/场景面试题/压力面试题
   - **出题范围**：仅技术面试/仅HR面试/全题型混合
   - **题目数量**：3-15道
4. 点击「📚 生成面试题」
5. 查看生成的面试题及标准答案
6. 复制或下载面试题库

## API参数配置详解

### API_BASE_URL

通义千问API的服务地址，一般不需要修改。

```
API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions
```

### API_MODEL

使用的模型名称，默认使用`qwen-plus`（通义千问Plus）。

可用的模型：
| 模型 | 说明 | 特点 |
|------|------|------|
| qwen-plus | 通义千问Plus | 效果较好，性价比高 |
| qwen-turbo | 通义千问Turbo | 速度快，费用低 |
| qwen-max | 通义千问Max | 效果最好，费用较高 |

### API_TIMEOUT

请求超时时间（秒），默认30秒。如果网络较慢可以适当调大。

### API_MAX_RETRIES

最大重试次数，默认3次。当API调用失败时，会自动重试。

## 常见问题

### Q: 启动报错"ModuleNotFoundError"

**A**: 确保已安装所有依赖，执行：

```bash
pip install streamlit python-dotenv requests
```

### Q: API调用失败"ConnectionError"

**A**: 检查网络连接，或可能是防火墙阻止。请确保能访问阿里云API服务。

### Q: 简历解析不准确

**A**: 请尽量使用格式规范的简历文本，避免使用特殊格式或图片。

### Q: 生成的面试题不符合预期

**A**: 可以调整左侧的难度、题型参数，或提供更详细的简历内容。

## 开发相关

### 运行测试

```bash
cd tests
python -m pytest
```

### 添加新的Prompt模板

编辑 `prompt_builder.py` 文件，按照现有格式添加新的Prompt函数。

### 修改API调用逻辑

编辑 `api_client.py` 文件，修改API调用相关函数。

## 免责声明

- 本系统生成的简历优化结果和面试题仅供参考
- 请勿将API密钥提交到公共代码仓库
- 用户需自行承担API调用费用

## License

MIT License