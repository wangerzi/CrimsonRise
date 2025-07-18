# coding:utf-8
from volcengine.visual.VisualService import VisualService
import streamlit as st
import os
import requests
from datetime import datetime
from config import VOLCENGINE_ACCESS_KEY, VOLCENGINE_SECRET_KEY

# pip install volcengine streamlit python-dotenv openai

# Initialize VisualService with config
visual_service = VisualService()
visual_service.set_ak(VOLCENGINE_ACCESS_KEY)
visual_service.set_sk(VOLCENGINE_SECRET_KEY)

# 创建保存目录
save_dir = "doubao_generated"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Streamlit App
st.title("🎨 通用 3.0 图像生成器")

# Add navigation info
st.markdown("**提示:** 如需生成红色年代海报，请运行 `streamlit run red_poster_generator.py`")
st.markdown("---")

# 分辨率选项配置
resolution_options = {
    "1.3K 分辨率 (推荐)": {
        "1:1 (1328×1328)": (1328, 1328),
        "4:3 (1472×1104)": (1472, 1104),
        "3:2 (1584×1056)": (1584, 1056),
        "16:9 (1664×936)": (1664, 936),
        "21:9 (2016×864)": (2016, 864)
    },
    "1.5K 分辨率": {
        "1:1 (1536×1536)": (1536, 1536),
        "4:3 (1472×1104)": (1472, 1104),
        "3:2 (1584×1056)": (1584, 1056),
        "16:9 (1664×936)": (1664, 936),
        "21:9 (2016×864)": (2016, 864)
    }
}

# Form for user input
with st.form("image_generation_form"):
    # Display parameter documentation link
    st.markdown("**参数文档参考:** [VolcEngine 图像生成 API 文档](https://www.volcengine.com/docs/85128/1526761)")
    
    # Request key fixed value
    req_key = st.text_input("算法名称 (req_key):", value="high_aes_general_v30l_zt2i", disabled=True)
    
    # Prompt
    prompt = st.text_area("提示词 (prompt):", placeholder="输入提示词以描述生成图的内容")
    
    # 分辨率选择
    st.subheader("📐 分辨率设置")
    st.info("推荐 1.3K ~1.5K 分辨率，画质更细腻，综合指标平衡得较好；1K 图和2K 图表现相对较弱")
    
    resolution_category = st.selectbox("选择分辨率档位:", list(resolution_options.keys()), index=0)
    ratio_option = st.selectbox("选择比例:", list(resolution_options[resolution_category].keys()), index=0)
    
    # 获取选中的宽高
    width, height = resolution_options[resolution_category][ratio_option]
    st.write(f"选中分辨率: {width}×{height}")
    
    # 生成数量
    num_images = st.number_input("生成图片数量:", min_value=1, max_value=10, value=4)
    
    # Whether to enable text expansion
    use_pre_llm = st.checkbox("开启文本扩写 (use_pre_llm)", value=False)
    
    # Random seed
    seed = st.number_input("随机种子 (seed):", min_value=-1, max_value=None, value=-1)
    
    # Text description degree
    scale = st.slider("文本描述程度 (scale):", min_value=1.0, max_value=10.0, value=2.5, step=0.1)
    
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

# 保存图片函数
def save_image(image_url, filename):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            filepath = os.path.join(save_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return filepath
        return None
    except Exception as e:
        st.error(f"保存图片失败: {e}")
        return None
    
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
    
    # 生成多张图片
    st.info(f"正在生成 {num_images} 张图片...")
    
    generated_images = []
    for i in range(num_images):
        try:
            # 如果设置了随机种子，为每张图片使用不同的种子
            if seed != -1:
                request_body["seed"] = seed + i
            
            response = visual_service.cv_process(request_body)
            
            # Parse return result
            if response.get("code") == 10000:
                image_urls = response["data"].get("image_urls", [])
                generated_images.extend(image_urls)
            else:
                st.error(f"第 {i+1} 张图片生成失败: {response.get('message')}")
        except Exception as e:
            st.error(f"第 {i+1} 张图片请求异常: {e}")
    
    if generated_images:
        st.success(f"成功生成 {len(generated_images)} 张图片!")
        
        # 显示生成的图片
        for idx, image_url in enumerate(generated_images):
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.image(image_url, caption=f"生成的图像 {idx + 1}")
            
            with col2:
                # 保存按钮
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{idx+1}.jpeg"
                
                if st.button(f"💾 保存图片 {idx + 1}", key=f"save_{idx}", help="点击保存到本地文件夹"):
                    filepath = save_image(image_url, filename)
                    if filepath:
                        st.success(f"✅ 已保存到: {filepath}")
                    else:
                        st.error("❌ 保存失败")
    else:
        st.warning("没有成功生成图片")
