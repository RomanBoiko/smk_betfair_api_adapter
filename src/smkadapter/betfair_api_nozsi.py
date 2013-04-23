from xmlrpclib import datetime
import logging
from lxml import etree
import os
import urllib2

from jinja2 import Template

from business_layer import BusinessUnit
import smk_api

ERROR_CODE_OK = "OK"
ERROR_INVALID_USERNAME_OR_PASSWORD = "INVALID_USERNAME_OR_PASSWORD"
ERROR_NO_SESSION = "NO_SESSION"
ERROR_API_ERROR = "API_ERROR"
ERROR_CANNOT_ACCEPT_BET = "CANNOT_ACCEPT_BET"
ERROR_BET_NOT_CANCELLED = "BET_NOT_CANCELLED"
ERROR_INVALID_MARKET = "INVALID_MARKET"

BUSINESS_UNIT = BusinessUnit()
LOGGER = logging.getLogger('[betfair.api]')

def readFile(path):
    fileStream = urllib2.urlopen("file://%s"%os.path.abspath(path))
    data = fileStream.read()
    fileStream.close()
    return data

def dispatchRequest(request):
    requestType = etree.XML(request).xpath("local-name(//*[local-name()='Body']/*[1])")
    if requestType=="login":
        return login(request)
    elif requestType=="getAllEventTypes":
        return getAllEventTypes(request)
    else:
        LOGGER.error("reqyest type %s could not be dispatched"%requestType)
        return "noAction"

def login(request):
    requestTree = etree.XML(request)
    username = requestTree.xpath("//*[local-name()='username']/text()")[0]
    password = requestTree.xpath("//*[local-name()='password']/text()")[0]
    template = Template(readFile("templates/login.response.xml"))

    loginResult = BUSINESS_UNIT.authenticateUserAndReturnHisSessionToken(username, password)
    if loginResult.succeeded :
        sessionToken = loginResult.result
        accountStatus = BUSINESS_UNIT.getAccountFunds(sessionToken)
        currency = accountStatus.currency
        return template.render(sessionId=sessionToken, errorCode=ERROR_CODE_OK, currency=currency)
    else:
        return template.render(sessionId="", errorCode=ERROR_INVALID_USERNAME_OR_PASSWORD, currency="")

def getAllEventTypes(request):
    requestTree = etree.XML(request)
    sessionId = requestTree.xpath("//*[local-name()='sessionToken']/text()")[0]
    template = Template(readFile("templates/getAllEventTypes.response.xml"))
    return template.render(sessionId=sessionId, eventTypeName="Football", eventTypeId=str(smk_api.FOOTBALL_EVENT_TYPE_ID))
