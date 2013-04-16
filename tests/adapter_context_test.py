import unittest

from smkadapter.adapter_context import *

class AdapterContextTest(unittest.TestCase):

    def assertPropertyWasSet(self, propertyValue):
        self.assertNotEqual(propertyValue, None, "Config value not found in context")
        self.assertNotEqual(propertyValue, "", "property is empty in config")

    def test_that_environment_was_set_up_for_testing(self):
        self.assertPropertyWasSet(OAUTH_CONSUMER_KEY)
        self.assertPropertyWasSet(OAUTH_CONSUMER_SECRET)
        self.assertPropertyWasSet(SMK_API_HOST)
        self.assertPropertyWasSet(SMK_API_PORT)
        self.assertPropertyWasSet(SMK_REST_API_PORT)
        self.assertPropertyWasSet(SMK_WEB_INTERFACE_PORT)
        self.assertPropertyWasSet(SMK_WEB_URL)
        self.assertPropertyWasSet(SMK_REST_API_URL)
        self.assertPropertyWasSet(SMK_OAUTH_AUTHORIZE_URL)
        self.assertPropertyWasSet(BETFAIR_API_PORT)
        self.assertPropertyWasSet(TEST_SMK_LOGIN)
        self.assertPropertyWasSet(TEST_SMK_PASSWORD)
