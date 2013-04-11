import os
import logging

logging.basicConfig(level=logging.DEBUG)#, filename="server.log", filemode="w"
from ConfigParser import SafeConfigParser

class Config(object):
    def __init__(self):
        self.configParser = SafeConfigParser()
        self.configParser.read('config/devenv.cfg')

    def defaultProperty(self, configKey):
        return self.configParser.get('default', configKey)

    def testProperty(self, configKey):
        return self.configParser.get('test', configKey)

config = Config()

OAUTH_CONSUMER_KEY = config.defaultProperty('OAUTH_CONSUMER_KEY')
OAUTH_CONSUMER_SECRET = config.defaultProperty('OAUTH_CONSUMER_SECRET')
SMK_API_HOST = config.defaultProperty('SMK_API_HOST')
SMK_API_PORT = config.defaultProperty('SMK_API_PORT')
SMK_REST_API_PORT = config.defaultProperty('SMK_REST_API_PORT')
SMK_WEB_INTERFACE_PORT = config.defaultProperty('SMK_WEB_INTERFACE_PORT')
SMK_WEB_URL = config.defaultProperty('SMK_WEB_URL')
SMK_REST_API_URL = config.defaultProperty('SMK_REST_API_URL')
SMK_OAUTH_AUTHORIZE_URL = config.defaultProperty('SMK_OAUTH_AUTHORIZE_URL')
BETFAIR_API_PORT = config.defaultProperty('BETFAIR_API_PORT')

TEST_SMK_LOGIN = config.testProperty('TEST_SMK_LOGIN')
TEST_SMK_PASSWORD = config.testProperty('TEST_SMK_PASSWORD')
SMK_TEST_CONTEXT = config.testProperty('SMK_TEST_CONTEXT')

def isAdapterRunningInTestContext():
    return SMK_TEST_CONTEXT == "true"
