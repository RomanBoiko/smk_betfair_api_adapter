import unittest
import smk_api
import time
import adapter_context

from smarkets.exceptions import SocketDisconnected
import session_management_actions

class ActionLoginTest(unittest.TestCase):

    def test_that_new_session_token_is_always_different(self):
        sessionToken1 = session_management_actions.newSessionId()
        sessionToken2 = session_management_actions.newSessionId()
        self.assertNotEquals(sessionToken1, sessionToken2)

    def test_that_session_token_length_equals_to_exposed_constant(self):
        self.assertEquals(len(session_management_actions.newSessionId()), session_management_actions.SESSION_TOKEN_LENGTH)

