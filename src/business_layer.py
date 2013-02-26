import uuid
import logging

import smarkets

import smk_api

DEFAULT_CURRENCY = "GBP"
FOOTBALL_EVENT_TYPE_ID = 121005


class Events(object):
    def __init__(self):
        self.parents = []
        self.parentToEvent={}
        self.eventToMarket={}

class Event(object):
    def __init__(self, eventId, eventName, eventTypeId):
        self.eventId = eventId
        self.eventName = eventName
        self.eventTypeId = eventTypeId

class Market(object):
    def __init__(self, marketId, marketName, marketTypeId, marketParentEventId):
        self.marketId = marketId
        self.marketName = marketName
        self.marketTypeId = marketTypeId
        self.marketParentEventId = marketParentEventId

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
            smk_api.logout(self.authenticatedClients[sessionToken])
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
        
    def getTodaysFootballEvents(self, sessionToken, eventParentId, eventConvertionFunction, marketConvertionFunction):
        if self.events is None :
            client = self.getClientIfTokenIsValid(sessionToken)
            eventsBroker = smk_api.EventsBroker()
            eventsMessage = eventsBroker.getEvents(client, smarkets.events.FootballByDate(smk_api.SmkDate()))
            self.events = self.loadEvents(eventsMessage, eventParentId, eventConvertionFunction, marketConvertionFunction)
        return self.events

    def loadEvents(self, eventsMessage, eventParentId, eventConvertionFunction, marketConvertionFunction):
        events = Events()
        for parent in eventsMessage.parents:
            eventDTO = Event(parent.event.low, parent.name, eventParentId)
            events.parents.append(eventConvertionFunction(eventDTO))
            events.parentToEvent[str(parent.event.low)]=[]
        for sportEvent in eventsMessage.with_markets:
            eventDTO = Event(sportEvent.event.low, sportEvent.name, FOOTBALL_EVENT_TYPE_ID)
            events.parentToEvent[str(sportEvent.parent.low)].append(eventConvertionFunction(eventDTO))
            events.eventToMarket[str(sportEvent.event.low)] = []
            for marketItem in sportEvent.markets :
                marketDTO = Market(marketItem.market.low, marketItem.name, FOOTBALL_EVENT_TYPE_ID, sportEvent.event.low)
                events.eventToMarket[str(sportEvent.event.low)].append(marketConvertionFunction(marketDTO))
        return events
