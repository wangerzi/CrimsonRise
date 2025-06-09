# coding:utf-8
import requests
import json
import time
import uuid
from io import BytesIO


class ComfyUIClient:
    """ComfyUI client for image upscaling"""
    
    def __init__(self, base_url="https://comfyui.internal.wj2015.com"):
        self.base_url = base_url.rstrip('/')
        
        # ComfyUI workflow template for upscaling
        self.upscale_workflow = {
            "2": {
                "inputs": {
                    "model_name": "RealESRGAN_x2.pth"
                },
                "class_type": "UpscaleModelLoader"
            },
            "4": {
                "inputs": {
                    "upscale_model": ["2", 0],
                    "image": ["5", 0]
                },
                "class_type": "ImageUpscaleWithModel"
            },
            "5": {
                "inputs": {
                    "image": "",  # Will be filled with uploaded image filename
                    "upload": "image"
                },
                "class_type": "LoadImage"
            },
            "7": {
                "inputs": {
                    "images": ["4", 0]
                },
                "class_type": "PreviewImage"
            }
        }
    
    def upload_image_from_url(self, image_url):
        """Upload image from URL to ComfyUI"""
        try:
            # Download image from URL
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Generate unique filename
            filename = f"{uuid.uuid4().hex}.jpeg"
            
            # Upload to ComfyUI
            files = {
                'image': (filename, BytesIO(response.content), 'image/jpeg')
            }
            
            upload_response = requests.post(
                f"{self.base_url}/upload/image",
                files=files,
                timeout=30
            )
            upload_response.raise_for_status()
            
            upload_result = upload_response.json()
            return upload_result.get('name', filename)
            
        except Exception as e:
            raise Exception(f"Failed to upload image from URL: {e}")
    
    def upload_image_from_bytes(self, image_bytes, original_filename=None):
        """Upload image from bytes data to ComfyUI"""
        try:
            # Generate unique filename
            if original_filename:
                # Keep original extension if available
                ext = original_filename.split('.')[-1].lower() if '.' in original_filename else 'jpeg'
                filename = f"{uuid.uuid4().hex}.{ext}"
            else:
                filename = f"{uuid.uuid4().hex}.jpeg"
            
            # Upload to ComfyUI
            files = {
                'image': (filename, BytesIO(image_bytes), 'image/jpeg')
            }
            
            upload_response = requests.post(
                f"{self.base_url}/upload/image",
                files=files,
                timeout=30
            )
            upload_response.raise_for_status()
            
            upload_result = upload_response.json()
            return upload_result.get('name', filename)
            
        except Exception as e:
            raise Exception(f"Failed to upload image from bytes: {e}")
    
    def upload_image(self, image_source):
        """Upload image to ComfyUI - supports both URL and bytes"""
        if isinstance(image_source, str):
            return self.upload_image_from_url(image_source)
        else:
            # Assume it's bytes or file-like object
            if hasattr(image_source, 'read'):
                # It's a file-like object
                image_bytes = image_source.read()
                filename = getattr(image_source, 'name', None)
                return self.upload_image_from_bytes(image_bytes, filename)
            else:
                # It's bytes
                return self.upload_image_from_bytes(image_source)
    
    def queue_prompt(self, workflow):
        """Queue workflow to ComfyUI"""
        try:
            payload = {"prompt": workflow}
            
            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get('prompt_id')
            
        except Exception as e:
            raise Exception(f"Failed to queue prompt: {e}")
    
    def get_history(self, prompt_id):
        """Get execution history for a prompt"""
        try:
            response = requests.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=30
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            raise Exception(f"Failed to get history: {e}")
    
    def get_image(self, filename, subfolder="", folder_type="output"):
        """Get processed image from ComfyUI"""
        try:
            params = {
                'filename': filename,
                'type': folder_type
            }
            if subfolder:
                params['subfolder'] = subfolder
            
            response = requests.get(
                f"{self.base_url}/view",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            raise Exception(f"Failed to get image: {e}")
    
    def wait_for_completion(self, prompt_id, timeout=300):
        """Wait for workflow completion and return result images"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                history = self.get_history(prompt_id)
                
                if prompt_id in history:
                    history_item = history[prompt_id]
                    
                    # Check if execution is complete
                    if 'outputs' in history_item:
                        outputs = history_item['outputs']
                        
                        # Look for PreviewImage output (node 7)
                        if "7" in outputs:
                            preview_output = outputs["7"]
                            if "images" in preview_output:
                                return preview_output["images"]
                
                time.sleep(2)  # Wait 2 seconds before checking again
                
            except Exception as e:
                print(f"Error checking status: {e}")
                time.sleep(2)
        
        raise Exception(f"Workflow timeout after {timeout} seconds")
    
    def upscale_image(self, image_source):
        """High-level method to upscale an image - supports URL, bytes, or file objects"""
        try:
            # Step 1: Upload image
            uploaded_filename = self.upload_image(image_source)
            
            # Step 2: Prepare workflow
            workflow = self.upscale_workflow.copy()
            workflow["5"]["inputs"]["image"] = uploaded_filename
            
            # Step 3: Queue workflow
            prompt_id = self.queue_prompt(workflow)
            
            if not prompt_id:
                raise Exception("Failed to get prompt ID")
            
            # Step 4: Wait for completion
            result_images = self.wait_for_completion(prompt_id)
            
            if not result_images:
                raise Exception("No output images found")
            
            # Step 5: Get the first result image
            first_image = result_images[0]
            image_data = self.get_image(
                first_image["filename"],
                first_image.get("subfolder", ""),
                first_image.get("type", "output")
            )
            
            return image_data
            
        except Exception as e:
            raise Exception(f"Upscale failed: {e}") 