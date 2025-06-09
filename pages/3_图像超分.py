# coding:utf-8
import streamlit as st
import base64
import requests
from PIL import Image
from io import BytesIO
from lib.comfyui_client import ComfyUIClient
from config import COMFYUI_BASE_URL

# Initialize ComfyUI client
@st.cache_resource
def init_comfyui_client():
    return ComfyUIClient(COMFYUI_BASE_URL)

comfyui_client = init_comfyui_client()

def download_button_for_image(image_data, filename):
    """Create download button for binary image data"""
    b64 = base64.b64encode(image_data).decode()
    href = f'<a href="data:image/jpeg;base64,{b64}" download="{filename}" style="display: inline-block; padding: 0.25rem 0.75rem; background-color: #ff4b4b; color: white; text-decoration: none; border-radius: 0.25rem; font-weight: 500;">📥 下载高清图片</a>'
    return href

def validate_image_url(url):
    """Validate if URL points to a valid image"""
    try:
        response = requests.head(url, timeout=10)
        content_type = response.headers.get('content-type', '').lower()
        return content_type.startswith('image/') and response.status_code == 200
    except:
        return False

def get_image_info(image_source):
    """Get image dimensions and format info"""
    try:
        if isinstance(image_source, str):  # URL
            response = requests.get(image_source, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
        else:  # Uploaded file
            image = Image.open(image_source)
        
        width, height = image.size
        format_name = image.format or "JPEG"
        
        return {
            "width": width,
            "height": height,
            "format": format_name,
            "size_mb": len(response.content) / (1024*1024) if isinstance(image_source, str) else image_source.size / (1024*1024)
        }
    except Exception as e:
        return {"error": str(e)}

# Streamlit App
st.title("🔍 图像超分辨率处理")
st.markdown("---")

# Description
st.markdown("""
**功能说明:** 使用 AI 技术将图像放大4倍，提升图像分辨率和清晰度。

**支持格式:** JPG, PNG, JPEG, WEBP  
**处理模型:** RealESRGAN_x2.pth (4倍超分辨率)

**使用方式:**
1. 上传本地图片文件 或 输入图片链接
2. 点击开始处理
3. 等待处理完成后下载高清图片
""")

# Input methods
st.subheader("📤 选择图片输入方式")
input_method = st.radio(
    "选择输入方式:",
    ["📁 上传本地文件", "🔗 输入图片链接"],
    horizontal=True
)

image_source = None
image_info = None

if input_method == "📁 上传本地文件":
    uploaded_file = st.file_uploader(
        "选择图片文件:",
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="支持 JPG、PNG、JPEG、WEBP 格式，建议文件大小不超过 10MB"
    )
    
    if uploaded_file:
        image_source = uploaded_file
        
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="原始图片", width=300)
        
        with col2:
            # Show image info
            image_info = get_image_info(uploaded_file)
            if "error" not in image_info:
                st.info(f"""
                📊 **图片信息:**
                - 尺寸: {image_info['width']} × {image_info['height']}
                - 格式: {image_info['format']}
                - 大小: {image_info['size_mb']:.2f} MB
                
                🎯 **处理后预期:**
                - 尺寸: {image_info['width']*4} × {image_info['height']*4}
                - 提升倍数: 4倍
                """)
            else:
                st.error(f"图片信息获取失败: {image_info['error']}")

else:  # URL input
    image_url = st.text_input(
        "输入图片链接:",
        placeholder="https://example.com/image.jpg",
        help="请输入有效的图片链接，支持 JPG、PNG、JPEG、WEBP 格式"
    )
    
    if image_url:
        if validate_image_url(image_url):
            image_source = image_url
            
            # Display image from URL
            col1, col2 = st.columns([1, 1])
            with col1:
                try:
                    st.image(image_url, caption="原始图片", width=300)
                except:
                    st.error("图片加载失败，请检查链接是否有效")
            
            with col2:
                # Show image info
                image_info = get_image_info(image_url)
                if "error" not in image_info:
                    st.info(f"""
                    📊 **图片信息:**
                    - 尺寸: {image_info['width']} × {image_info['height']}
                    - 格式: {image_info['format']}
                    - 大小: {image_info['size_mb']:.2f} MB
                    
                    🎯 **处理后预期:**
                    - 尺寸: {image_info['width']*4} × {image_info['height']*4}
                    - 提升倍数: 4倍
                    """)
                else:
                    st.error(f"图片信息获取失败: {image_info['error']}")
        else:
            st.warning("⚠️ 请输入有效的图片链接")

# Processing section
st.markdown("---")
st.subheader("🚀 开始处理")

if image_source:
    # Processing options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("🔧 **处理设置:**\n- 超分模型: RealESRGAN_x2.pth\n- 放大倍数: 4倍\n- 预计处理时间: 30-120秒")
    
    with col2:
        process_button = st.button("🎨 开始超分处理", type="primary", use_container_width=True)
    
    if process_button:
        try:
            with st.spinner("🔄 正在上传图片并处理，请稍候..."):
                # Handle different input types - now both URL and file upload are supported
                upscaled_image_data = comfyui_client.upscale_image(image_source)
                
                # Display results
                st.success("✅ 图像超分处理完成!")
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.subheader("📷 原始图片")
                    if isinstance(image_source, str):
                        st.image(image_source, width=300)
                    else:
                        st.image(image_source, width=300)
                
                with col2:
                    st.subheader("✨ 高清图片")
                    st.image(upscaled_image_data, width=600)
                
                # Download section
                st.markdown("---")
                st.subheader("📥 下载高清图片")
                
                # Create download link
                download_link = download_button_for_image(
                    upscaled_image_data, 
                    f"upscaled_image_4x.jpg"
                )
                st.markdown(download_link, unsafe_allow_html=True)
                
                # Processing stats
                if image_info and "error" not in image_info:
                    st.success(f"""
                    🎯 **处理完成统计:**
                    - 原始尺寸: {image_info['width']} × {image_info['height']}
                    - 处理后尺寸: {image_info['width']*4} × {image_info['height']*4}
                    - 像素提升: {((image_info['width']*4 * image_info['height']*4) / (image_info['width'] * image_info['height'])):.1f}倍
                    """)
                    
        except Exception as e:
            st.error(f"❌ 图像处理失败: {e}")
            st.info("💡 请检查：\n- 图片链接是否有效\n- 网络连接是否正常\n- ComfyUI 服务是否可用")

else:
    st.info("👆 请先选择要处理的图片")

# Additional info
st.markdown("---")
with st.expander("ℹ️ 技术说明"):
    st.markdown("""
    **超分辨率技术:**
    - 使用 RealESRGAN 模型进行图像超分辨率处理
    - 基于生成对抗网络(GAN)技术
    - 专门针对真实图像场景进行优化
    
    **处理流程:**
    1. 图片上传到 ComfyUI 服务器
    2. 加载 RealESRGAN_x2.pth 模型
    3. 执行4倍超分辨率处理
    4. 返回高清图片结果
    
    **最佳效果建议:**
    - 原图分辨率建议在 200×200 以上
    - 图片清晰度越高，效果越好
    - 避免过度压缩的图片
    """)

st.markdown("---")
st.caption("🤖 Powered by ComfyUI & RealESRGAN") 