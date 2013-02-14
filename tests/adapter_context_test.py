from adapter_context import *
import unittest

class AdapterContextTest(unittest.TestCase):

    def test_that_environment_was_set_up_for_testing(self):
        variableNotSetMessage = "ENV Variable not set"
        self.assertNotEqual(SMK_LOGIN, None, variableNotSetMessage)
        self.assertNotEqual(SMK_PASSWORD, None, variableNotSetMessage)
