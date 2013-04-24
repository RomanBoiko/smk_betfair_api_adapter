import logging

logging.basicConfig(level=logging.DEBUG)#, filename="server.log", filemode="w"
logging.getLogger('smarkets').setLevel(logging.INFO)
from ConfigParser import SafeConfigParser

class Config(object):
    def __init__(self):
        self.configParser = SafeConfigParser()
        self.configParser.read('config/sandbox.cfg')

    def defaultProperty(self, configKey):
        return self.configParser.get('default', configKey)

    def testProperty(self, configKey):
        return self.configParser.get('test', configKey)

config = Config()

OAUTH_CONSUMER_KEY = config.defaultProperty('oauth.consumer.key')
OAUTH_CONSUMER_SECRET = config.defaultProperty('oauth.consumer.secret')
SMK_API_HOST = config.defaultProperty('smk.api.host')
SMK_API_PORT = config.defaultProperty('smk.api.port')
SMK_REST_API_PORT = config.defaultProperty('smk.rest.api.port')
SMK_WEB_INTERFACE_PORT = config.defaultProperty('smk.web.interface.port')
SMK_WEB_URL = config.defaultProperty('smk.web.url')
SMK_REST_API_URL = config.defaultProperty('smk.rest.api.url')
SMK_OAUTH_AUTHORIZE_URL = config.defaultProperty('smk.oauth.authorize.url')
BETFAIR_API_PORT = config.defaultProperty('betfair.api.port')

TEST_SMK_LOGIN = config.testProperty('test.smk.login')
TEST_SMK_PASSWORD = config.testProperty('test.smk.password')
