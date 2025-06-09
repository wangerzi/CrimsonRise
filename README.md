# AI图像生成平台

基于火山引擎的AI图像生成平台，包含通用图像生成器和红色年代海报生成器。

<img width="1401" alt="image" src="https://github.com/user-attachments/assets/42329709-f7c0-41cc-8c28-4b5ce0377ab6" />

<img width="1439" alt="image" src="https://github.com/user-attachments/assets/27d17506-d21b-4e81-831e-d367ffa5b9f9" />


## 功能特性

- 🎨 **通用图像生成器**: 支持全参数配置的图像生成
- 🚩 **红色年代海报生成器**: 基于AI生成复古大字报风格海报

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置环境变量

1. 复制 `.env.example` 为 `.env`
2. 填入您的配置信息：

```env
# 火山引擎配置
VOLCENGINE_ACCESS_KEY=your_volcengine_access_key_here
VOLCENGINE_SECRET_KEY=your_volcengine_secret_key_here

# OpenAI 配置 (用于调用 Doubao)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# Doubao 模型配置
DOUBAO_MODEL=doubao-1-5-pro-32k-250115
```

## 运行应用

### 方式一：运行主应用（推荐）
```bash
streamlit run main.py
```

## 使用说明

### 红色年代海报生成器

1. 输入创意描述，例如："几位劳动者在工厂工作"
2. 设置生成数量和图片尺寸
3. 点击生成按钮
4. AI会自动生成符合红色年代风格的提示词，然后生成海报

**示例:**
- 输入: "几位劳动者在工厂工作"
- AI生成: "生成几位分别在挥拳、前冲、吹冲锋号、办公的劳动者作为主体，复古大字报风格的插画，背景是工厂机械，底部是'劳动最光荣'"

### 通用图像生成器

支持全参数配置，包括：
- 提示词设置
- 图像尺寸调整
- 随机种子控制
- 水印设置
- 等更多高级参数

## 技术架构

- **前端**: Streamlit
- **图像生成**: 火山引擎 VisualService API
- **AI提示词生成**: 通过 OpenAI API 调用火山豆包模型
- **配置管理**: python-dotenv

## 注意事项

1. 确保正确配置火山引擎的 Access Key 和 Secret Key
2. 如使用红色年代海报生成器，需配置 OpenAI API Key 用于调用豆包模型
3. 建议使用 `.env` 文件管理敏感配置信息 
