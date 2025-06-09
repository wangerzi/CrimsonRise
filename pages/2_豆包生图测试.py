# coding:utf-8
from volcengine.visual.VisualService import VisualService
import streamlit as st
from config import VOLCENGINE_ACCESS_KEY, VOLCENGINE_SECRET_KEY

# pip install volcengine streamlit python-dotenv openai

# Initialize VisualService with config
visual_service = VisualService()
visual_service.set_ak(VOLCENGINE_ACCESS_KEY)
visual_service.set_sk(VOLCENGINE_SECRET_KEY)

# Streamlit App
st.title("🎨 通用 3.0 图像生成器")

# Add navigation info
st.markdown("**提示:** 如需生成红色年代海报，请运行 `streamlit run red_poster_generator.py`")
st.markdown("---")

# Form for user input
with st.form("image_generation_form"):
    # Display parameter documentation link
    st.markdown("**参数文档参考:** [VolcEngine 图像生成 API 文档](https://www.volcengine.com/docs/85128/1526761)")
    
    # Request key fixed value
    req_key = st.text_input("算法名称 (req_key):", value="high_aes_general_v30l_zt2i", disabled=True)
    
    # Prompt
    prompt = st.text_area("提示词 (prompt):", placeholder="输入提示词以描述生成图的内容")
    
    # Whether to enable text expansion
    use_pre_llm = st.checkbox("开启文本扩写 (use_pre_llm)", value=False)
    
    # Random seed
    seed = st.number_input("随机种子 (seed):", min_value=-1, max_value=None, value=-1)
    
    # Text description degree
    scale = st.slider("文本描述程度 (scale):", min_value=1.0, max_value=10.0, value=2.5, step=0.1)
    
    # Image width
    width = st.number_input("图像宽度 (width):", min_value=512, max_value=2048, value=1328, step=1)
    
    # Image height
    height = st.number_input("图像高度 (height):", min_value=512, max_value=2048, value=1328, step=1)
    
    # Whether to return URL
    return_url = st.checkbox("返回图片链接 (return_url)", value=True)
    
    # Watermark related parameters
    st.subheader("水印设置 (可选)")
    add_logo = st.checkbox("添加水印 (add_logo)", value=False)
    position = st.selectbox("水印位置 (position):", options=[0, 1, 2, 3], format_func=lambda x: ["右下角", "左下角", "左上角", "右上角"][x], index=0)
    language = st.selectbox("水印语言 (language):", options=[0, 1], format_func=lambda x: ["中文", "英文"][x], index=0)
    opacity = st.slider("水印不透明度 (opacity):", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
    logo_text_content = st.text_input("自定义水印内容 (logo_text_content):", "")
    
    # Submit button
    submitted = st.form_submit_button("生成图像")
    
# If form is submitted
if submitted:
    # Construct request body
    request_body = {
        "req_key": req_key,
        "prompt": prompt,
        "use_pre_llm": use_pre_llm,
        "seed": seed,
        "scale": scale,
        "width": width,
        "height": height,
        "return_url": return_url,
        "logo_info": {
            "add_logo": add_logo,
            "position": position,
            "language": language,
            "opacity": opacity,
            "logo_text_content": logo_text_content
        }
    }
    
    # Remove unnecessary watermark fields (if watermark is not enabled)
    if not add_logo:
        request_body.pop("logo_info", None)
    
    # Call API to generate image
    try:
        response = visual_service.cv_process(request_body)
        st.success("请求成功!")
        
        # Parse return result
        if response.get("code") == 10000:
            generated_images = response["data"].get("image_urls", [])
            for idx, image_url in enumerate(generated_images):
                st.image(image_url, caption=f"生成的图像 {idx + 1}")
        else:
            st.error(f"生成失败: {response.get('message')}")
    except Exception as e:
        st.error(f"请求异常: {e}")
