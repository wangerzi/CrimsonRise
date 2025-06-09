import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Volcengine configuration
VOLCENGINE_ACCESS_KEY = os.getenv('VOLCENGINE_ACCESS_KEY', '')
VOLCENGINE_SECRET_KEY = os.getenv('VOLCENGINE_SECRET_KEY', '')

# OpenAI configuration for Doubao
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
DOUBAO_MODEL = os.getenv('DOUBAO_MODEL', 'doubao-1-5-pro-32k-250115') 