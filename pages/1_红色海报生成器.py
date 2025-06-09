# coding:utf-8
import streamlit as st
import requests
import json
from volcengine.visual.VisualService import VisualService
from config import VOLCENGINE_ACCESS_KEY, VOLCENGINE_SECRET_KEY, OPENAI_API_KEY, OPENAI_BASE_URL, DOUBAO_MODEL

# Initialize Visual Service
visual_service = VisualService()
visual_service.set_ak(VOLCENGINE_ACCESS_KEY)
visual_service.set_sk(VOLCENGINE_SECRET_KEY)

# Predefined aspect ratios and corresponding dimensions
ASPECT_RATIOS = {
    "1:1 (正方形)": (1328, 1328),
    "4:3 (标准)": (1472, 1104),
    "3:2 (经典)": (1584, 1056),
    "16:9 (宽屏)": (1664, 936),
    "21:9 (超宽屏)": (2016, 864)
}

def generate_poster_prompt(user_prompt):
    """Use Doubao to generate poster-style prompt via direct HTTP request"""
    try:
        # Prepare request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # Prepare request payload
        payload = {
            "model": DOUBAO_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "你是一个专业的红色年代海报设计师。请根据用户输入的内容，生成一个复古大字报风格的插画描述。格式必须是：'生成[合适的主体描述]作为主体，复古大字报风格的插画，背景是[相关背景元素]，底部是[相关标语]'。要体现红色年代的热情、团结、奋进精神，不要出现敏感内容如人民、革命等"
                },
                {
                    "role": "user",
                    "content": f"请为以下内容生成红色年代海报风格的提示词：{user_prompt}"
                }
            ],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        # Make HTTP request
        response = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        result = response.json()
        return result["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.RequestException as e:
        st.error(f"网络请求失败: {e}")
        raise e
    except KeyError as e:
        st.error(f"响应格式错误: {e}")
        raise e
    except Exception as e:
        st.error(f"生成提示词失败: {e}")
        raise e

def generate_images(prompt, count, width, height):
    """Generate images using Volcengine API"""
    try:
        request_body = {
            "req_key": "high_aes_general_v30l_zt2i",
            "prompt": prompt,
            "use_pre_llm": False,
            "seed": -1,
            "scale": 2.5,
            "width": width,
            "height": height,
            "return_url": True,
        }
        
        images = []
        for i in range(count):
            response = visual_service.cv_process(request_body)
            if response.get("code") == 10000:
                generated_images = response["data"].get("image_urls", [])
                images.extend(generated_images)
            else:
                st.error(f"第{i+1}张图片生成失败: {response.get('message')}")
        
        return images
    except Exception as e:
        st.error(f"图片生成异常: {e}")
        return []

# Streamlit App
st.title("🚩 红色年代海报生成器")
st.markdown("---")

# Description
st.markdown("""
**功能说明:** 输入您的创意想法，AI将自动生成符合红色年代风格的海报提示词，然后生成复古大字报风格的插画。

**示例输入:** "几位劳动者在工厂工作"  
**AI会生成类似:** "生成几位分别在挥拳、前冲、吹冲锋号、办公的劳动者作为主体，复古大字报风格的插画，背景是工厂机械，底部是'劳动最光荣'"
""")

with st.form("red_poster_form"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # User input prompt
        user_prompt = st.text_area(
            "📝 输入您的创意描述:", 
            placeholder="例如: 为豆包服务\n让豆包再次伟大\n为豆包点赞",
            height=100
        )
    
    with col2:
        # Image count
        image_count = st.number_input("🖼️ 生成数量:", min_value=1, max_value=4, value=1)
        
        # Image aspect ratio selection
        st.subheader("📐 图片比例")
        selected_ratio = st.selectbox(
            "选择比例:",
            options=list(ASPECT_RATIOS.keys()),
            index=0,  # Default to 1:1
            help="选择适合的图片比例，每种比例都有对应的最佳尺寸"
        )
        
        # Get dimensions based on selected ratio
        width, height = ASPECT_RATIOS[selected_ratio]
        
        # Display selected dimensions
        st.info(f"📏 尺寸: {width} × {height}")
    
    # Submit button
    submitted = st.form_submit_button("🎨 生成红色年代海报", use_container_width=True)

if submitted and user_prompt:
    with st.spinner("正在生成红色年代风格提示词..."):
        # Generate poster prompt using Doubao
        poster_prompt = generate_poster_prompt(user_prompt)
        
        st.success("✅ AI生成的海报提示词:")
        st.info(poster_prompt)
    
    with st.spinner("正在生成海报图片..."):
        # Generate images
        generated_images = generate_images(poster_prompt, image_count, width, height)
        
        if generated_images:
            st.success(f"🎉 成功生成 {len(generated_images)} 张红色年代海报!")
            
            # Display images in columns
            cols = st.columns(min(len(generated_images), 4))
            for idx, image_url in enumerate(generated_images):
                with cols[idx % 4]:
                    st.image(image_url, caption=f"红色年代海报 {idx + 1}", width=512)
        else:
            st.error("❌ 图片生成失败，请检查配置或重试")

elif submitted and not user_prompt:
    st.warning("⚠️ 请输入您的创意描述") 