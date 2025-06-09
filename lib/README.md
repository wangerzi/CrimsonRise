# Lib 模块说明

## 概述
该目录包含了海报生成器的核心业务逻辑，已抽象为可复用的类。

## 模块结构

### `poster_generator.py`
红色年代海报生成器的核心类
- **PosterGenerator**: 主要功能类
  - `generate_prompt()`: 使用豆包AI生成海报风格提示词
  - `generate_images()`: 使用火山引擎生成图片
  - `get_aspect_ratios()`: 获取可用的图片比例选项

### `comfyui_client.py`
ComfyUI 客户端，用于图片高清化处理
- **ComfyUIClient**: ComfyUI API 客户端
  - `upscale_image()`: 图片高清化主要接口
  - `upload_image()`: 上传图片到ComfyUI
  - `queue_prompt()`: 提交工作流到队列
  - `wait_for_completion()`: 等待处理完成
  - `get_image()`: 获取处理后的图片

## 使用示例

```python
from lib.poster_generator import PosterGenerator
from lib.comfyui_client import ComfyUIClient

# 初始化海报生成器
poster_gen = PosterGenerator(ak, sk, api_key, base_url, model)

# 生成提示词
prompt = poster_gen.generate_prompt("为豆包服务")

# 生成图片
images = poster_gen.generate_images(prompt, 1, 1328, 1328)

# 高清化图片
comfyui = ComfyUIClient("https://comfyui.internal.wj2015.com")
hd_image = comfyui.upscale_image(images[0])
```

## 配置说明
所有配置项都在 `config.py` 中定义，包括：
- 火山引擎API密钥
- OpenAI/豆包API配置
- ComfyUI服务地址 