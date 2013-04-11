from __future__ import unicode_literals

import unittest
import requests
from urlparse import parse_qs
from requests_oauthlib import OAuth1
import re
import mechanize

import smkadapter.adapter_context as adapter_context

class RestApiAuthenticationIntegrationTest(unittest.TestCase):
    def test_rest_authentication_on_local_smk_env(self):
        API = adapter_context.SMK_REST_API_URL
        AUTHORIZE_URL = adapter_context.SMK_OAUTH_AUTHORIZE_URL

        oauth = OAuth1(adapter_context.OAUTH_CONSUMER_KEY, adapter_context.OAUTH_CONSUMER_SECRET)#instructions how to retreive at https://wiki.corp.smarkets.com/wiki/Adding_an_OAuth_Client

        result = requests.post('%s/request_token' % API, auth=oauth)
        response = parse_qs(unicode(result.text))
        # print "Now visit %s?oauth_token=%s to authorize" % (AUTHORIZE_URL, response['oauth_token'][0])
        verifier = self.smarkets_auth("%s?oauth_token=%s"%(AUTHORIZE_URL, response['oauth_token'][0]))
        oauth.client.resource_owner_key = response['oauth_token'][0]
        oauth.client.resource_owner_secret = response['oauth_token_secret'][0]
        oauth.client.verifier = unicode(verifier.strip())

        result = requests.post('%s/access_token' % API, auth=oauth)
        response = parse_qs(unicode(result.text))

        oauth.client.resource_owner_key = response['oauth_token'][0]
        oauth.client.resource_owner_secret = response['oauth_token_secret'][0]
        oauth.client.verifier = None

        result = requests.get('%s/ping' % API, auth=oauth)

    def smarkets_auth(self, authorisationUrlToFollow):
        br = mechanize.Browser()
        br.set_handle_robots(False)
        br.open(adapter_context.SMK_WEB_URL)

        br.select_form(nr=0)
        br["email"] = adapter_context.TEST_SMK_LOGIN
        br["password"] = adapter_context.TEST_SMK_PASSWORD
        br.submit()
        html = br.open(authorisationUrlToFollow)
        resultsBeforeApprove = html.read().decode("ascii", "ignore")
        br.select_form(nr=0)
        resultsAfterApprove = br.submit(name='action', label='Approve').read().decode("ascii", "ignore")
        m = re.search("(?<=<p>Please enter the code )(.+?)(?= into Client Name in order to grant it access.</p>)", resultsAfterApprove)
        return m.group(0)

if __name__ == "__main__":
    RestApiAuthenticationIntegrationTest().test_rest_authentication_on_local_smk_env()