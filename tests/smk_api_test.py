import unittest
import smk_api
import time
import adapter_context

from smarkets.exceptions import SocketDisconnected

class SmkApiTest(unittest.TestCase):

    def test_that_smk_api_must_login_and_logout_successfuly(self):
        client = smk_api.login(adapter_context.SMK_LOGIN, adapter_context.SMK_PASSWORD)
        smk_api.logout(client)
        
    def test_that_smk_api_must_thow_SocketDisconnected_exception_if_credentials_are_wrong(self):
        try:
            #using different login to avoid user blocking
            smk_api.login('wrongLogin_' + str(time.time()), 'wrongPassword')
        except SocketDisconnected:
            assert True
        else:
            assert False

