import unittest
import smk_api
import time
import adapter_context

from smarkets.exceptions import SocketDisconnected
import action_login

class ActionLoginTest(unittest.TestCase):

    def test_that_new_session_token_is_always_different(self):
        sessionToken1 = action_login.newSessionId()
        sessionToken2 = action_login.newSessionId()
        self.assertNotEquals(sessionToken1, sessionToken2)

    def test_that_session_token_length_equals_to_exposed_constant(self):
        self.assertEquals(len(action_login.newSessionId()), action_login.SESSION_TOKEN_LENGTH)

