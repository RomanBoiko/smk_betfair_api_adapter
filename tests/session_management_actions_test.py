import unittest
import smk_api
import time
import adapter_context

from smarkets.exceptions import SocketDisconnected
import session_management_actions
from session_management_actions import SessionStorage

class SessionStorageTest(unittest.TestCase):
    storage = SessionStorage()

    def test_that_new_session_token_is_always_different(self):
        sessionToken1 = self.storage.newSessionId()
        sessionToken2 = self.storage.newSessionId()
        self.assertNotEquals(sessionToken1, sessionToken2)

    def test_that_session_token_length_equals_to_exposed_constant(self):
        self.assertEquals(len(self.storage.newSessionId()), self.storage.SESSION_TOKEN_LENGTH)
    
    def test_that_SessionStorage_is_singleton_and_is_not_instantiated_twice(self):
        self.assertEquals(id(SessionStorage()), id(self.storage))
