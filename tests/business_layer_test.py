import time
import unittest

import smkadapter.adapter_context as adapter_context
import smkadapter.smk_api as smk_api
from smkadapter.business_layer import SessionStorage

from smarkets.exceptions import SocketDisconnected

class SessionStorageTest(unittest.TestCase):
    storage = SessionStorage()

    def test_that_new_session_token_is_always_different(self):
        sessionToken1 = self.storage.newSessionId()
        sessionToken2 = self.storage.newSessionId()
        self.assertNotEquals(sessionToken1, sessionToken2)

    def test_that_session_token_length_equals_to_exposed_constant(self):
        self.assertEquals(len(self.storage.newSessionId()), self.storage.SESSION_TOKEN_LENGTH)
