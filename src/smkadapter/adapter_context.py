import os
import logging

logging.basicConfig(level=logging.DEBUG)#, filename="server.log", filemode="w"

TEST_SMK_LOGIN    = os.getenv("TEST_SMK_LOGIN")
TEST_SMK_PASSWORD = os.getenv("TEST_SMK_PASSWORD")
SMK_API_HOST      = os.getenv("SMK_API_HOST", "api-sandbox.smarkets.com")
SMK_API_PORT      = os.getenv("SMK_API_PORT", "3701")
BETFAIR_API_PORT  = os.getenv("BETFAIR_API_PORT", "8080")

def isAdapterRunningInTestContext():
	return (os.getenv("SMK_TEST_CONTEXT") is not None)