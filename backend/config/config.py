# coding=utf-8

import os

from dotenv import load_dotenv

load_dotenv(dotenv_path="backend/.env")


class Config:
    
    # NOTE: Dify Configurations
    DIFY_CONFIG = {
        "base_url": os.getenv("DIFY_BASE_URL", "https://api.dify.ai"),
        "api_key": os.getenv("DIFY_API_KEY"),
        "user": os.getenv("DIFY_USER"),
    }
    
CONFIG = Config()