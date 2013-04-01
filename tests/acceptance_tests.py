import httplib
import time
import unittest
from xml.dom.minidom import parseString

import smkadapter.adapter_context as adapter_context
import smkadapter.betfair_api as betfair_api
import smkadapter.smk_api as smk_api

HOST="localhost"
PORT=int(adapter_context.BETFAIR_API_PORT)
BETFAIR_GLOBAL_SERVICE = "/BFGlobalService"
BETFAIR_EXCHANGE_SERVICE = "/BFExchangeService"

ERROR_CODE_TAG="errorCode"
SESSION_TOKEN_TAG="sessionToken"

SOAP_ENVELOPE = """<?xml version="1.0" encoding="UTF-8"?>
                    <soapenv:Envelope 
                            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                            xmlns:bfg="http://www.betfair.com/publicapi/v3/BFGlobalService/"
                            xmlns:bfex="http://www.betfair.com/publicapi/v5/BFExchangeService/"
                            xmlns:v5="http://www.betfair.com/publicapi/types/exchange/v5/">
                       <soapenv:Header/>
                       <soapenv:Body>%s</soapenv:Body>
                    </soapenv:Envelope>
                """

loginRequestTemplate = """<bfg:login>
                             <bfg:request>
                                <ipAddress>0</ipAddress>
                                <locationId>0</locationId>
                                <password>%s</password>
                                <productId>82</productId>
                                <username>%s</username>
                                <vendorSoftwareId>0</vendorSoftwareId>
                             </bfg:request>
                          </bfg:login>"""

logoutRequestTemplate = """<bfg:logout>
                             <bfg:request>
                                <header>
                                   <clientStamp>0</clientStamp>
                                   <sessionToken>%s</sessionToken>
                                </header>
                             </bfg:request>
                          </bfg:logout>"""

getEventsRequestTemplate = """<bfg:getEvents>
                                 <bfg:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <eventParentId>%s</eventParentId>
                                    <locale>en_UK</locale>
                                 </bfg:request>
                              </bfg:getEvents>"""

getAllEventTypesRequestTemplate = """<bfg:getAllEventTypes>
                                 <bfg:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <locale>en_UK</locale>
                                 </bfg:request>
                              </bfg:getAllEventTypes>"""
                              
getAccountFundsRequestTemplate = """<bfex:getAccountFunds>
                                         <bfex:request>
                                            <header>
                                               <clientStamp>0</clientStamp>
                                               <sessionToken>%s</sessionToken>
                                            </header>
                                         </bfex:request>
                                      </bfex:getAccountFunds>"""
                                      
placeBetsRequestTemplate = """<bfex:placeBets>
                                 <bfex:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <bets>
                                       <!--Zero or more repetitions:-->
                                       <v5:PlaceBets>
                                          <asianLineId>0</asianLineId><!-- 0 for non-Asian, asianId for AsianHandicap -->
                                          <betType>B</betType><!-- or L -->
                                          <betCategoryType>E</betCategoryType><!-- or M or L -->
                                          <betPersistenceType>NONE</betPersistenceType><!-- or IP or SP -->
                                          <marketId>%s</marketId>
                                          <price>%s</price>
                                          <selectionId>%s</selectionId>
                                          <size>%s</size>
                                          <bspLiability>%s</bspLiability>
                                       </v5:PlaceBets>
                                    </bets>
                                 </bfex:request>
                              </bfex:placeBets>"""
                              
cancelBetsRequestTemplate = """<bfex:cancelBets>
                                 <bfex:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <bets>
                                       <!--Zero or more repetitions:-->
                                       <v5:CancelBets>
                                          <betId>%s</betId>
                                       </v5:CancelBets>
                                    </bets>
                                 </bfex:request>
                              </bfex:cancelBets>"""

getCurrentBetsRequestTemplate = """<bfex:getCurrentBets>
                                     <bfex:request>
                                        <header>
                                           <clientStamp>0</clientStamp>
                                           <sessionToken>%s</sessionToken>
                                        </header>
                                        <betStatus>UM</betStatus><!-- matched/unmatched -->
                                        <detailed>false</detailed><!-- show matches or not -->
                                        <locale>en_UK</locale>
                                        <timezone>GMT</timezone>
                                        <marketId>123</marketId><!-- we can avoid mentioning that -->
                                        <orderBy>NONE</orderBy>
                                        <recordCount>10000</recordCount>
                                        <startRecord>0</startRecord>
                                        <noTotalRecordCount>true</noTotalRecordCount>
                                     </bfex:request>
                                  </bfex:getCurrentBets>"""

#Planned
cancelBetsByMarketRequestTemplate = """<bfex:cancelBetsByMarket>
                                   <bfex:request>
                                      <header>
                                         <clientStamp>0</clientStamp>
                                         <sessionToken>%s</sessionToken>
                                      </header>
                                      <markets>
                                         <!--Zero or more repetitions:-->
                                         <v5:int>%s</v5:int>
                                         <v5:int>%s</v5:int>
                                      </markets>
                                   </bfex:request>
                                </bfex:cancelBetsByMarket>"""

getMarketRequestTemplate = """<bfex:getMarket>
                               <bfex:request>
                                  <header>
                                     <clientStamp>0</clientStamp>
                                     <sessionToken>%s</sessionToken>
                                  </header>
                                  <locale>en_UK</locale>
                                  <marketId>%s</marketId>
                                  <includeCouponLinks>false</includeCouponLinks>
                               </bfex:request>
                            </bfex:getMarket>"""

##########################
################TO REPLACE
getMarketPricesRequestTemplate = """<bfex:getMarketPrices>
                                       <bfex:request>
                                          <header>
                                             <clientStamp>0</clientStamp>
                                             <sessionToken>%s</sessionToken>
                                          </header>
                                          <currencyCode>GBP</currencyCode>
                                          <marketId>%s</marketId>
                                       </bfex:request>
                                    </bfex:getMarketPrices>"""

getMarketPricesCompressedRequestTemplate = """<bfex:getMarketPricesCompressed>
                                                 <bfex:request>
                                                    <header>
                                                       <clientStamp>0</clientStamp>
                                                       <sessionToken>%s</sessionToken>
                                                    </header>
                                                    <currencyCode>GBP</currencyCode>
                                                    <marketId>%s</marketId>
                                                 </bfex:request>
                                              </bfex:getMarketPricesCompressed>"""

getMarketTradedVolumeRequestTemplate = """<bfex:getMarketTradedVolume>
                                             <bfex:request>
                                                <header>
                                                   <clientStamp>0</clientStamp>
                                                   <sessionToken>%s</sessionToken>
                                                </header>
                                                <asianLineId>0</asianLineId>
                                                <currencyCode>GBP</currencyCode>
                                                <marketId>%s</marketId>
                                                <selectionId>%s</selectionId>
                                             </bfex:request>
                                          </bfex:getMarketTradedVolume>"""

getMarketTradedVolumeCompressedRequestTemplate = """<bfex:getMarketTradedVolumeCompressed>
                                                       <bfex:request>
                                                          <header>
                                                             <clientStamp>0</clientStamp>
                                                             <sessionToken>%s</sessionToken>
                                                          </header>
                                                          <currencyCode>GBP</currencyCode>
                                                          <marketId>%s</marketId>
                                                       </bfex:request>
                                                    </bfex:getMarketTradedVolumeCompressed>"""

updateBetsRequestTemplate = """<bfex:updateBets>
                                 <bfex:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <bets>
                                       <!--Zero or more repetitions:-->
                                       <v5:UpdateBets>
                                          <betId>111111</betId>                               <!-- <xsd:element name="betId" type="xsd:long"/>                                    -->
                                          <newPrice>1.0</newPrice>                            <!-- <xsd:element name="newPrice" nillable="true" type="xsd:double"/>               -->
                                          <newSize>1.0</newSize>                              <!-- <xsd:element name="newSize" nillable="false" type="xsd:double"/>               -->
                                          <oldPrice>1.0</oldPrice>                            <!-- <xsd:element name="oldPrice" nillable="true" type="xsd:double"/>               -->
                                          <oldSize>1.0</oldSize>                              <!-- <xsd:element name="oldSize" nillable="false" type="xsd:double"/>               -->
                                          <oldBetPersistenceType>NONE</oldBetPersistenceType> <!-- <xsd:element name="oldBetPersistenceType" type="types:BetPersistenceTypeEnum"/>-->
                                          <newBetPersistenceType>NONE</newBetPersistenceType> <!-- <xsd:element name="newBetPersistenceType" type="types:BetPersistenceTypeEnum"/>-->
                                       </v5:UpdateBets>
                                    </bets>
                                 </bfex:request>
                              </bfex:updateBets>"""

getMUBetsRequestTemplate = """<bfex:getMUBets>
                                 <bfex:request>
                                    <header>
                                       <clientStamp>0</clientStamp>
                                       <sessionToken>%s</sessionToken>
                                    </header>
                                    <betStatus>MU</betStatus><!-- <xsd:simpleType name="BetStatusEnum"> -->
                                    <marketId>111111</marketId>
                                    <betIds>
                                       <!--0 to 1000 repetitions:-->
                                       <!--<v5:betId>111111</v5:betId>-->
                                    </betIds>
                                    <orderBy>BET_ID</orderBy>
                                    <sortOrder>ASC</sortOrder>
                                    <recordCount>1000</recordCount>
                                    <startRecord>0</startRecord>
                                    <matchedSince/>
                                    <excludeLastSecond>false</excludeLastSecond>
                                 </bfex:request>
                              </bfex:getMUBets>"""

getBetRequestTemplate = """<bfex:getBet>
                             <bfex:request>
                                <header>
                                   <clientStamp>0</clientStamp>
                                   <sessionToken>%s</sessionToken>
                                </header>
                                <betId>%s</betId>
                                <locale>en_UK</locale>
                             </bfex:request>
                          </bfex:getBet>"""

getAllMarketsRequestTemplate = """<bfex:getAllMarkets>
                                     <bfex:request>
                                        <header>
                                           <clientStamp>0</clientStamp>
                                           <sessionToken>%s</sessionToken>
                                        </header>
                                        <locale>en_UK</locale>
                                        <eventTypeIds>
                                           <!--Zero or more repetitions:-->
                                           <!-- <v5:int>?</v5:int> -->
                                        </eventTypeIds>
                                        <countries>
                                           <!--Zero or more repetitions:-->
                                           <!-- <v5:Country>?</v5:Country> -->
                                        </countries>
                                        <fromDate/>
                                        <toDate/>
                                     </bfex:request>
                                  </bfex:getAllMarkets>"""

getBetHistoryRequestTemplate = """<bfex:getBetHistory>
                                     <bfex:request>
                                        <header>
                                           <clientStamp>0</clientStamp>
                                           <sessionToken>%s</sessionToken>
                                        </header>
                                        <betTypesIncluded>%s</betTypesIncluded> <!-- <xsd:element name="betTypesIncluded" type="types:BetStatusEnum"/> -->
                                        <detailed>false</detailed>
                                        <eventTypeIds>
                                           <!--Zero or more repetitions:-->
                                           <!--<v5:int>?</v5:int>-->
                                        </eventTypeIds>
                                        <marketId>%s</marketId>
                                        <locale>en_UK</locale>
                                        <timezone/>
                                        <marketTypesIncluded>
                                           <!--Zero or more repetitions:-->
                                           <!-- <v5:MarketTypeEnum>?</v5:MarketTypeEnum> -->
                                        </marketTypesIncluded>
                                        <placedDateFrom>2013-03-27T21:32:52</placedDateFrom> <!-- <xsd:element name="placedDateFrom" type="xsd:dateTime"/>            -->
                                        <placedDateTo>2013-03-27T21:32:52</placedDateTo>     <!-- <xsd:element name="placedDateTo" type="xsd:dateTime"/>              -->
                                        <recordCount>1111111</recordCount>                   <!-- <xsd:element name="recordCount" nillable="false" type="xsd:int"/>   -->
                                        <sortBetsBy>BET_ID</sortBetsBy>                      <!-- <xsd:element name="sortBetsBy" type="types:BetsOrderByEnum"/>       -->
                                        <startRecord>0</startRecord>                         <!-- <xsd:element name="startRecord" nillable="false" type="xsd:int"/>   -->
                                     </bfex:request>
                                  </bfex:getBetHistory>"""

getInPlayMarketsRequestTemplate = """<bfex:getInPlayMarkets>
                                       <bfex:request>
                                          <header>
                                             <clientStamp>0</clientStamp>
                                             <sessionToken>%s</sessionToken>
                                          </header>
                                          <locale>en_UK</locale>
                                       </bfex:request>
                                    </bfex:getInPlayMarkets>"""

getAccountStatementRequestTemplate = """<bfex:getAccountStatement>
                                           <bfex:req>
                                              <header>
                                                 <clientStamp>0</clientStamp>
                                                 <sessionToken>%s</sessionToken>
                                              </header>
                                              <endDate>2013-03-27T21:32:52</endDate>           <!-- <xsd:element name="endDate" type="xsd:dateTime"/>                             -->
                                              <itemsIncluded>ALL</itemsIncluded>               <!-- <xsd:element name="itemsIncluded" type="types:AccountStatementIncludeEnum"/>  -->
                                              <ignoreAutoTransfers>false</ignoreAutoTransfers> <!-- <xsd:element name="ignoreAutoTransfers" nillable="false" type="xsd:boolean"/> -->
                                              <recordCount>100000</recordCount>                <!-- <xsd:element name="recordCount" nillable="false" type="xsd:int"/>             -->
                                              <startDate>2013-03-27T21:32:52</startDate>       <!-- <xsd:element name="startDate" type="xsd:dateTime"/>                           -->
                                              <startRecord>0</startRecord>                     <!-- <xsd:element name="startRecord" nillable="false" type="xsd:int"/>             -->
                                              <locale>en_UK</locale>
                                           </bfex:req>
                                        </bfex:getAccountStatement>"""

class AdapterAcceptanceTest(unittest.TestCase):
    def assertErrorCodeInHeaderIs(self, response, expectedErrorCode):
        self.assertEquals(textFromElement(response, ERROR_CODE_TAG, 0), expectedErrorCode)
    def assertResultErrorCodeIs(self, response, expectedErrorCode):
        self.assertEquals(textFromElement(response, ERROR_CODE_TAG, 1), expectedErrorCode)
    def assertErrorCodesAreOk(self, responseDom):
        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_CODE_OK)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)

class SessionManagementAcceptanceTest(AdapterAcceptanceTest):

    def test_that_valid_credentials_are_causing_successful_login(self):
        responseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)
        sessionToken = sessionTokenFrom(responseDom)
        self.assertGreater(len(sessionToken), 0)

        getLogoutResponseDom(sessionToken)

    def test_that_invalid_credentials_are_causing_login_failure(self):
        responseDom = getLoginResponseDom('wrongLogin_' + str(time.time()), 'wrongPassword')

        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_INVALID_USERNAME_OR_PASSWORD)
        self.assertEquals(responseDom.getElementsByTagName(SESSION_TOKEN_TAG)[0].firstChild, None)

    def test_that_logout_with_nonexisting_session_token_results_unsuccessfuly(self):
        responseDom = getLogoutResponseDom("invalidSessionToken")
        #THEN
        self.assertErrorCodeInHeaderIs(responseDom, betfair_api.ERROR_NO_SESSION)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_API_ERROR)

    def test_that_logout_with_valid_session_token_results_successfuly(self):
        loginResponseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        validSessionToken = sessionTokenFrom(loginResponseDom)
        logoutResponseDom = getLogoutResponseDom(validSessionToken)
        #THEN
        self.assertErrorCodesAreOk(logoutResponseDom)


class WorkflowTest(AdapterAcceptanceTest):

    @classmethod
    def setUpClass(cls):
        loginResponseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        WorkflowTest.validSessionToken = sessionTokenFrom(loginResponseDom)

    @classmethod
    def tearDownClass(cls):
        getLogoutResponseDom(WorkflowTest.validSessionToken)

    def test_that_fixed_dummy_list_of_event_types_is_returned(self):
        request = soapMessage(getAllEventTypesRequestTemplate%(WorkflowTest.validSessionToken))
        responseDom = parseString(getGlobalServiceReply(request))
        self.assertEqual(textFromElement(responseDom, "name", 0), "Football")
        self.assertEqual(textFromElement(responseDom, "id", 0), str(smk_api.FOOTBALL_EVENT_TYPE_ID))
        self.assertErrorCodesAreOk(responseDom)



    def test_that_list_of_football_parent_events_is_in_reponse_on_events_by_football_parentid(self):
        footballEventTypeId = str(smk_api.FOOTBALL_EVENT_TYPE_ID)
        request = soapMessage(getEventsRequestTemplate%(WorkflowTest.validSessionToken, footballEventTypeId))
        responseXml = getGlobalServiceReply(request)
        responseDom = parseString(responseXml)

        self.validateEventTypeAndParentIds(responseDom, footballEventTypeId, footballEventTypeId)
        self.assertErrorCodesAreOk(responseDom)

        self.check_that_event_children_can_be_retreived_by_getEvents_request(self.firstEventId(responseDom), footballEventTypeId)

    def check_that_event_children_can_be_retreived_by_getEvents_request(self, parentEventId, eventTypeId):
        request = soapMessage(getEventsRequestTemplate%(WorkflowTest.validSessionToken, parentEventId))
        responseXml = getGlobalServiceReply(request)
        responseDom = parseString(responseXml)

        self.validateEventTypeAndParentIds(responseDom, eventTypeId, parentEventId)

        self.check_that_markets_can_be_retreived_by_getEvents_request(self.firstEventId(responseDom), eventTypeId)


    def check_that_markets_can_be_retreived_by_getEvents_request(self, parentEventId, eventTypeId):
        request = soapMessage(getEventsRequestTemplate%(WorkflowTest.validSessionToken, parentEventId))
        responseXml = getGlobalServiceReply(request)
        responseDom = parseString(responseXml)

        self.validateEventTypeAndParentIds(responseDom, eventTypeId, parentEventId)

        self.check_that_contracts_can_be_retreived_by_getEvents_request(self.firstEventId(responseDom), eventTypeId)

    def check_that_contracts_can_be_retreived_by_getEvents_request(self, parentEventId, eventTypeId):
        request = soapMessage(getEventsRequestTemplate%(WorkflowTest.validSessionToken, parentEventId))
        responseXml = getGlobalServiceReply(request)
        responseDom = parseString(responseXml)

        self.validateEventTypeAndParentIds(responseDom, eventTypeId, parentEventId)
        self.assertEqual(textFromElement(responseDom, "eventParentId", 1), parentEventId)
        firstMarketId = textFromElement(responseDom, "marketId", 0)
        self.assertGreater(len(firstMarketId), 0)

        self.check_that_exchange_service_placesBets(parentEventId, firstMarketId)

    def firstEventId(self, responseDom):
        return textFromElement(responseDom, "eventId", 0)

    def validateEventTypeAndParentIds(self, responseDom, eventTypeId, parentEventId):
        self.assertEqual(textFromElement(responseDom, "eventParentId", 0), parentEventId)
        self.assertEqual(textFromElement(responseDom, "eventTypeId", 0), eventTypeId)

    def check_that_exchange_service_placesBets(self, marketId, contractId):
        priceInProcents=2500
        quantityInPounds = 3

        request = soapMessage(placeBetsRequestTemplate%(WorkflowTest.validSessionToken, marketId, priceInProcents, contractId, quantityInPounds, quantityInPounds))
        responseXml = getExchangeServiceReply(request)
        responseDom = parseString(responseXml)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)
        self.assertEqual(textFromElement(responseDom, "averagePriceMatched", 0), str(quantityInPounds)+".000000")
        self.assertEqual(textFromElement(responseDom, "sizeMatched", 0), str(quantityInPounds)+".000000")
        self.assertEqual(textFromElement(responseDom, "success", 0), "true")
        betId = textFromElement(responseDom, "betId", 0)
        self.assertTrue(len(betId)>0)

        getBetsResponseDom = self.getListOfBetsForAccount()
        self.assertEqual(textFromElement(getBetsResponseDom, "betId", 0), betId)
        self.assertEqual(textFromElement(responseDom, "resultCode", 0), betfair_api.ERROR_CODE_OK)

        self.exchange_service_should_cancel_bet_using_cancelBets(betId)

    def exchange_service_should_cancel_bet_using_cancelBets(self, betId):
        request = soapMessage(cancelBetsRequestTemplate%(WorkflowTest.validSessionToken, betId))
        responseXml = getExchangeServiceReply(request)
        responseDom = parseString(responseXml)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)
        self.assertEqual(textFromElement(responseDom, "success", 0), "true")
        self.assertEqual(textFromElement(responseDom, "betId", 0), str(betId))

    def test_that_placeBets_with_unexisting_marketId_returns_action_failed_response(self):
        priceInProcents=2500
        quantityInPounds = 3

        unexistingMarketId = 0
        unexistingContractId = 0
        request = soapMessage(placeBetsRequestTemplate%(WorkflowTest.validSessionToken, unexistingMarketId, priceInProcents, unexistingContractId, quantityInPounds, quantityInPounds))
        responseXml = getExchangeServiceReply(request)
        responseDom = parseString(responseXml)
        self.assertEqual(textFromElement(responseDom, "resultCode", 0), betfair_api.ERROR_CANNOT_ACCEPT_BET)
        self.assertEqual(textFromElement(responseDom, "success", 0), "false")
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)

    def test_that_cancelBets_with_unexisting_betId_returns_action_failed_response(self):
        unexistingBetId = 0
        request = soapMessage(cancelBetsRequestTemplate%(WorkflowTest.validSessionToken, unexistingBetId))
        responseXml = getExchangeServiceReply(request)
        responseDom = parseString(responseXml)
        self.assertEqual(textFromElement(responseDom, "success", 0), "false")
        self.assertEqual(textFromElement(responseDom, "resultCode", 0), betfair_api.ERROR_BET_NOT_CANCELLED)
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)

    def test_exchange_service_getAccountFunds(self):
        request = soapMessage(getAccountFundsRequestTemplate%(WorkflowTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        responseDom = parseString(responseXml)
 
        for balanceField in ["balance", "availBalance", "withdrawBalance"]:
            self.assertEqual(textFromElement(responseDom, balanceField, 0), "10.000000")

    def test_that_list_of_bets_is_returned_for_account(self):
        responseDom = self.getListOfBetsForAccount()
        self.assertResultErrorCodeIs(responseDom, betfair_api.ERROR_CODE_OK)

    def getListOfBetsForAccount(self):
        request = soapMessage(getCurrentBetsRequestTemplate%(WorkflowTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        return parseString(responseXml)

class RequestsResponsesValidationTest(AdapterAcceptanceTest):

    @classmethod
    def setUpClass(cls):
        loginResponseDom = getLoginResponseDom(adapter_context.TEST_SMK_PASSWORD, adapter_context.TEST_SMK_LOGIN)
        RequestsResponsesValidationTest.validSessionToken = sessionTokenFrom(loginResponseDom)

    @classmethod
    def tearDownClass(cls):
        getLogoutResponseDom(RequestsResponsesValidationTest.validSessionToken)

    def test_exchange_service_getMUBets(self):
        request = soapMessage(getMUBetsRequestTemplate%(RequestsResponsesValidationTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        print "============getMUBets: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getBet(self):
        betId = 84181761152778484
        request = soapMessage(getBetRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, betId))
        responseXml = getExchangeServiceReply(request)
        print "============getBet: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getBetHistory(self):
        betTypesIncluded = "M"
        marketId = 276267
        request = soapMessage(getBetHistoryRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, betTypesIncluded, marketId))
        responseXml = getExchangeServiceReply(request)
        print "============getBetHistory: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_cancelBetsByMarket(self):
        testMarket1 = 276267
        testMarket2 = 1111111

        request = soapMessage(cancelBetsByMarketRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, testMarket1, testMarket2))
        responseXml = getExchangeServiceReply(request)
        print "============CANCEL_BY_MARKET: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getMarket(self):
        testMarketId = 1111111

        request = soapMessage(getMarketRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, testMarketId))
        responseXml = getExchangeServiceReply(request)
        print "============GET_MARKET: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getMarketPrices(self):
        marketId = 1111111
        request = soapMessage(getMarketPricesRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, marketId))
        responseXml = getExchangeServiceReply(request)
        print "============getMarketPrices: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getMarketPricesCompressed(self):
        marketId = 1111111
        request = soapMessage(getMarketPricesCompressedRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, marketId))
        responseXml = getExchangeServiceReply(request)
        print "============getMarketPricesCompressed: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getMarketTradedVolume(self):
        marketId = 1111111
        contractId = 1111111
        request = soapMessage(getMarketTradedVolumeRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, marketId, contractId))
        responseXml = getExchangeServiceReply(request)
        print "============getMarketTradedVolume: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getMarketTradedVolumeCompressed(self):
        marketId = 1111111
        request = soapMessage(getMarketTradedVolumeCompressedRequestTemplate%(RequestsResponsesValidationTest.validSessionToken, marketId))
        responseXml = getExchangeServiceReply(request)
        print "============getMarketTradedVolumeCompressed: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_updateBets(self):
        request = soapMessage(updateBetsRequestTemplate%(RequestsResponsesValidationTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        print "============updateBets: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getAllMarkets(self):
        request = soapMessage(getAllMarketsRequestTemplate%(RequestsResponsesValidationTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        print "============getAllMarkets: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getInPlayMarkets(self):
        request = soapMessage(getInPlayMarketsRequestTemplate%(RequestsResponsesValidationTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        print "============getInPlayMarkets: %s"%responseXml
        responseDom = parseString(responseXml)

    def test_exchange_service_getAccountStatement(self):
        request = soapMessage(getAccountStatementRequestTemplate%(RequestsResponsesValidationTest.validSessionToken))
        responseXml = getExchangeServiceReply(request)
        print "============getAccountStatement: %s"%responseXml
        responseDom = parseString(responseXml)

###############################################
# Common utils to operate with Betfair SOAP API
###############################################

def getServerReply(request, serviceName):
    http_conn = httplib.HTTP(HOST, PORT)
    http_conn.putrequest('POST', serviceName)
    http_conn.putheader('Host', HOST)
    http_conn.putheader('Content-Type', 'text/xml; charset="utf-8"')
    http_conn.putheader('Content-Length', str(len(request)))
    http_conn.putheader('SOAPAction', '')
    http_conn.endheaders()
    http_conn.send(request)
    (status_code, message, reply_headers) = http_conn.getreply() 
    response = http_conn.getfile().read() 
    return response

def getGlobalServiceReply(request):
    return getServerReply(request, BETFAIR_GLOBAL_SERVICE)

def getExchangeServiceReply(request):
    return getServerReply(request, BETFAIR_EXCHANGE_SERVICE)

def getLogoutResponseDom(sessionToken):
    logoutRequest = soapMessage(logoutRequestTemplate%(sessionToken))
    return parseString(getGlobalServiceReply(logoutRequest))

def getLoginResponseDom(username, password):
    loginRequest = soapMessage(loginRequestTemplate%(username, password))
    response = getGlobalServiceReply(loginRequest)
    return parseString(response)

def textFromElement(dom, elementName, elementPosition):
    return dom.getElementsByTagName(elementName)[elementPosition].firstChild.nodeValue

def sessionTokenFrom(response):
    return textFromElement(response, SESSION_TOKEN_TAG, 0)

def soapMessage(body):
    return SOAP_ENVELOPE%(body)
