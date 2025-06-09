# coding:utf-8
import requests
import json
from volcengine.visual.VisualService import VisualService


class PosterGenerator:
    """Red era poster generation service"""
    
    def __init__(self, volcengine_ak, volcengine_sk, openai_api_key, openai_base_url, doubao_model):
        # Initialize Visual Service
        self.visual_service = VisualService()
        self.visual_service.set_ak(volcengine_ak)
        self.visual_service.set_sk(volcengine_sk)
        
        # API configuration
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url
        self.doubao_model = doubao_model
        
        # Predefined aspect ratios and corresponding dimensions
        self.aspect_ratios = {
            "1:1 (正方形)": (1328, 1328),
            "4:3 (标准)": (1472, 1104),
            "3:2 (经典)": (1584, 1056),
            "16:9 (宽屏)": (1664, 936),
            "21:9 (超宽屏)": (2016, 864)
        }
    
    def generate_prompt(self, user_prompt):
        """Use Doubao to generate poster-style prompt via direct HTTP request"""
        try:
            # Prepare request headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            # Prepare request payload
            payload = {
                "model": self.doubao_model,
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
                f"{self.openai_base_url}/chat/completions",
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
            raise Exception(f"Network request failed: {e}")
        except KeyError as e:
            raise Exception(f"Response format error: {e}")
        except Exception as e:
            raise Exception(f"Generate prompt failed: {e}")
    
    def generate_images(self, prompt, count, width, height):
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
                response = self.visual_service.cv_process(request_body)
                if response.get("code") == 10000:
                    generated_images = response["data"].get("image_urls", [])
                    images.extend(generated_images)
                else:
                    raise Exception(f"Image {i+1} generation failed: {response.get('message')}")
            
            return images
        except Exception as e:
            raise Exception(f"Image generation failed: {e}")
    
    def get_aspect_ratios(self):
        """Get available aspect ratios"""
        return self.aspect_ratios 