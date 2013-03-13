import uuid
import logging
import datetime

import smk_api

DEFAULT_CURRENCY = "GBP"


class SessionStorage(object):
    "Encapsulates client authentication actions and active clients storage"
    SESSION_TOKEN_LENGTH=32
    LOGGER = logging.getLogger('[session.storage]')

    def __init__(self):
        self.authenticatedClients = {}
        self.LOGGER.info("empty Smarkets SessionStorage started ")

    def newSessionId(self):
        return uuid.uuid4().hex
    
    def authenticateUserAndReturnHisSessionToken(self, username, password):
        client = smk_api.login(username, password)
        sessionToken = self.newSessionId()
        self.authenticatedClients[sessionToken] = client
        return sessionToken

    def getClientIfTokenIsValid(self, sessionToken):
        if sessionToken in self.authenticatedClients :
            return self.authenticatedClients[sessionToken]
        else :
            return None
    
    def logUserOutAndReturnResultOfAction(self, sessionToken):
        if sessionToken in self.authenticatedClients :
            self.authenticatedClients[sessionToken].logout()
            del self.authenticatedClients[sessionToken]
            return True
        else:
            return False

class BusinessUnit(object):
    LOGGER = logging.getLogger('[business.unit]')
    
    def __init__(self):
        self.sessionStorage = SessionStorage()
        self.authenticateUserAndReturnHisSessionToken = self.sessionStorage.authenticateUserAndReturnHisSessionToken
        self.logUserOutAndReturnResultOfAction = self.sessionStorage.logUserOutAndReturnResultOfAction
        self.getClientIfTokenIsValid = self.sessionStorage.getClientIfTokenIsValid
        self.LOGGER.info("BusinessUnit started ")
        self.events = None
        
    def getTodaysFootballEvents(self, sessionToken):
        if self.events is None :
            client = self.getClientIfTokenIsValid(sessionToken)
            self.events = client.footballByDate(datetime.date.today())
        return self.events

    def getAccountFunds(self, sessionToken):
        client = self.getClientIfTokenIsValid(sessionToken)
        return client.getAccountState()

    def placeBet(self, sessionToken, marketId, contractId, quantity, price):
        client = self.getClientIfTokenIsValid(sessionToken)
        return client.placeBet(marketId, contractId, quantity, price)

    def cancelBet(self, sessionToken, orderId):
        client = self.getClientIfTokenIsValid(sessionToken)
        return client.cancelBet(orderId)

    def getBetsForAccount(self, sessionToken):
        client = self.getClientIfTokenIsValid(sessionToken)
        return client.getBetsForAccount()

