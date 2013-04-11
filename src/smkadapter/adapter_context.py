import os
import logging

logging.basicConfig(level=logging.DEBUG)#, filename="server.log", filemode="w"

TEST_SMK_LOGIN        = os.getenv("TEST_SMK_LOGIN")
TEST_SMK_PASSWORD     = os.getenv("TEST_SMK_PASSWORD")

OAUTH_CONSUMER_KEY    = os.getenv("OAUTH_CONSUMER_KEY")
OAUTH_CONSUMER_SECRET = os.getenv("OAUTH_CONSUMER_SECRET")

SMK_API_HOST          = os.getenv("SMK_API_HOST", "vagrant-dev.corp.smarkets.com")#api-sandbox.smarkets.com
SMK_API_PORT          = os.getenv("SMK_API_PORT", "3700")
SMK_REST_API_PORT     = os.getenv("SMK_REST_API_PORT", "8007")
SMK_WEB_INTERFACE_PORT= os.getenv("SMK_WEB_INTERFACE_PORT", "8091")

SMK_WEB_URL = "http://%s:%s" % (SMK_API_HOST, SMK_WEB_INTERFACE_PORT)
SMK_REST_API_URL = "http://%s:%s" % (SMK_API_HOST, SMK_REST_API_PORT)
SMK_OAUTH_AUTHORIZE_URL = "%s/account/applications/authorize" % (SMK_WEB_URL)

BETFAIR_API_PORT      = os.getenv("BETFAIR_API_PORT", "8888")

def isAdapterRunningInTestContext():
	return (os.getenv("SMK_TEST_CONTEXT") is not None)