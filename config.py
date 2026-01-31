import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Grist Config
    GRIST_BASE_URL = os.getenv('GRIST_BASE_URL')
    GRIST_DOC_ID = os.getenv('GRIST_DOC_ID')
    GRIST_API_KEY = os.getenv('GRIST_API_KEY')
    GRIST_TABLE = os.getenv('GRIST_TABLE')
    
    # DN Config
    DN_API_URL = os.getenv('DN_API_URL')
    DN_TOKEN = os.getenv('DN_TOKEN')
    INSTRUCTEUR_ID = os.getenv('INSTRUCTEUR_ID')