import sys
import logging

logging.basicConfig(level=logging.DEBUG)#, filename="server.log", filemode="w"
logging.getLogger('smarkets').setLevel(logging.DEBUG)
from ConfigParser import SafeConfigParser

LOG = logging.getLogger('[adapter_context]')

class Config(object):
    def __init__(self):
        if len(sys.argv) < 2 or ("cfg" not in sys.argv[1]):
            LOG.warn("==>config location not specified: using config/sandbox.cfg as default")
            self.configLocation = 'config/sandbox.cfg'
        else:
            self.configLocation = sys.argv[1]
            LOG.info("==>using config from %s"%self.configLocation)
        self.configParser = SafeConfigParser()
        self.configParser.read(self.configLocation)

    def defaultProperty(self, configKey):
        return self.configParser.get('default', configKey)

    def testProperty(self, configKey):
        return self.configParser.get('test', configKey)

config = Config()

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
