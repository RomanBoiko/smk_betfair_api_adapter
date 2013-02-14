import os

SMK_LOGIN        = os.getenv("SMK_LOGIN")
SMK_PASSWORD     = os.getenv("SMK_PASSWORD")
SMK_API_HOST     = os.getenv("SMK_API_HOST", "api-sandbox.smarkets.com")
SMK_API_PORT     = os.getenv("SMK_API_PORT", "3701")
BETFAIR_API_PORT = os.getenv("BETFAIR_API_PORT", "8080")
