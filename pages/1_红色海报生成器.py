# coding:utf-8
import streamlit as st
from lib.poster_generator import PosterGenerator
from config import (
    VOLCENGINE_ACCESS_KEY, 
    VOLCENGINE_SECRET_KEY, 
    OPENAI_API_KEY, 
    OPENAI_BASE_URL, 
    DOUBAO_MODEL
)

# Initialize services
@st.cache_resource
def init_services():
    poster_gen = PosterGenerator(
        VOLCENGINE_ACCESS_KEY,
        VOLCENGINE_SECRET_KEY,
        OPENAI_API_KEY,
        OPENAI_BASE_URL,
        DOUBAO_MODEL
    )
    return poster_gen

poster_generator = init_services()

# Streamlit App
st.title("🚩 红色年代海报生成器")
st.markdown("---")

# Description
st.markdown("""
**功能说明:** 输入您的创意想法，AI将自动生成符合红色年代风格的海报提示词，然后生成复古大字报风格的插画。

**示例输入:** "几位劳动者在工厂工作"  
**AI会生成类似:** "生成几位分别在挥拳、前冲、吹冲锋号、办公的劳动者作为主体，复古大字报风格的插画，背景是工厂机械，底部是'劳动最光荣'"

💡 **提示:** 如需高清化处理，可将生成的图片链接复制到 [🔍 图像超分] 页面进行处理。
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
        aspect_ratios = poster_generator.get_aspect_ratios()
        selected_ratio = st.selectbox(
            "选择比例:",
            options=list(aspect_ratios.keys()),
            index=0,  # Default to 1:1
            help="选择适合的图片比例，每种比例都有对应的最佳尺寸"
        )
        
        # Get dimensions based on selected ratio
        width, height = aspect_ratios[selected_ratio]
        
        # Display selected dimensions
        st.info(f"📏 尺寸: {width} × {height}")
    
    # Submit button
    submitted = st.form_submit_button("🎨 生成红色年代海报", use_container_width=True)

if submitted and user_prompt:
    with st.spinner("正在生成红色年代风格提示词..."):
        try:
            # Generate poster prompt
            poster_prompt = poster_generator.generate_prompt(user_prompt)
            st.success("✅ AI生成的海报提示词:")
            st.info(poster_prompt)
        except Exception as e:
            st.error(f"❌ 提示词生成失败: {e}")
            st.stop()
    
    with st.spinner("正在生成海报图片..."):
        try:
            # Generate images
            generated_images = poster_generator.generate_images(poster_prompt, image_count, width, height)
            
            if generated_images:
                st.success(f"🎉 成功生成 {len(generated_images)} 张红色年代海报!")
                
                # Display images in columns
                cols = st.columns(min(len(generated_images), 4))
                for idx, image_url in enumerate(generated_images):
                    with cols[idx % 4]:
                        st.image(image_url, caption=f"红色年代海报 {idx + 1}", width=256)
                        
                        # Add copy URL button for each image
                        with st.expander(f"📋 图片链接 {idx + 1}"):
                            st.code(image_url, language=None)
                            st.caption("💡 复制此链接到 [🔍 图像超分] 页面进行高清化处理")
                            
                # High-resolution processing tip
                st.markdown("---")
                st.info("🔍 **想要更高清的图片？** 复制上面的图片链接，前往 [🔍 图像超分] 页面进行4倍超分辨率处理！")
                            
            else:
                st.error("❌ 图片生成失败，请重试")
        except Exception as e:
            st.error(f"❌ 图片生成失败: {e}")

elif submitted and not user_prompt:
    st.warning("⚠️ 请输入您的创意描述") 