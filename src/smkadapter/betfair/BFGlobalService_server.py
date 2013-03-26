##################################################
# file: BFGlobalService_server.py
#
# skeleton generated by "ZSI.generate.wsdl2dispatch.ServiceModuleWriter"
#      /usr/local/bin/wsdl2py BFGlobalService.wsdl
#
##################################################

from ZSI.schema import GED, GTD
from BFGlobalService_types import *
from ZSI.ServiceContainer import ServiceSOAPBinding
import betfair_api

# Messages  
loginIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "login").pyclass

loginOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "loginResponse").pyclass

retrieveLIMBMessageIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "retrieveLIMBMessage").pyclass

retrieveLIMBMessageOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "retrieveLIMBMessageResponse").pyclass

submitLIMBMessageIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "submitLIMBMessage").pyclass

submitLIMBMessageOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "submitLIMBMessageResponse").pyclass

logoutIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "logout").pyclass

logoutOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "logoutResponse").pyclass

keepAliveIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "keepAlive").pyclass

keepAliveOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "keepAliveResponse").pyclass

getEventsIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getEvents").pyclass

getEventsOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getEventsResponse").pyclass

getActiveEventTypesIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getActiveEventTypes").pyclass

getActiveEventTypesOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getActiveEventTypesResponse").pyclass

getAllEventTypesIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getAllEventTypes").pyclass

getAllEventTypesOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getAllEventTypesResponse").pyclass

getSubscriptionInfoIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getSubscriptionInfo").pyclass

getSubscriptionInfoOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getSubscriptionInfoResponse").pyclass

depositFromPaymentCardIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "depositFromPaymentCard").pyclass

depositFromPaymentCardOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "depositFromPaymentCardResponse").pyclass

addPaymentCardIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "addPaymentCard").pyclass

addPaymentCardOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "addPaymentCardResponse").pyclass

deletePaymentCardIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "deletePaymentCard").pyclass

deletePaymentCardOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "deletePaymentCardResponse").pyclass

updatePaymentCardIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "updatePaymentCard").pyclass

updatePaymentCardOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "updatePaymentCardResponse").pyclass

getPaymentCardIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getPaymentCard").pyclass

getPaymentCardOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getPaymentCardResponse").pyclass

withdrawToPaymentCardIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "withdrawToPaymentCard").pyclass

withdrawToPaymentCardOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "withdrawToPaymentCardResponse").pyclass

selfExcludeIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "selfExclude").pyclass

selfExcludeOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "selfExcludeResponse").pyclass

convertCurrencyIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "convertCurrency").pyclass

convertCurrencyOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "convertCurrencyResponse").pyclass

getAllCurrenciesIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getAllCurrencies").pyclass

getAllCurrenciesOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getAllCurrenciesResponse").pyclass

getAllCurrenciesV2In = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getAllCurrenciesV2").pyclass

getAllCurrenciesV2Out = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "getAllCurrenciesV2Response").pyclass

viewReferAndEarnIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "viewReferAndEarn").pyclass

viewReferAndEarnOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "viewReferAndEarnResponse").pyclass

viewProfileIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "viewProfile").pyclass

viewProfileOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "viewProfileResponse").pyclass

viewProfileV2In = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "viewProfileV2").pyclass

viewProfileV2Out = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "viewProfileV2Response").pyclass

modifyProfileIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "modifyProfile").pyclass

modifyProfileOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "modifyProfileResponse").pyclass

createAccountIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "createAccount").pyclass

createAccountOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "createAccountResponse").pyclass

forgotPasswordIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "forgotPassword").pyclass

forgotPasswordOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "forgotPasswordResponse").pyclass

modifyPasswordIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "modifyPassword").pyclass

modifyPasswordOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "modifyPasswordResponse").pyclass

withdrawByBankTransferIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "withdrawByBankTransfer").pyclass

withdrawByBankTransferOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "withdrawByBankTransferResponse").pyclass

setChatNameIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "setChatName").pyclass

setChatNameOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "setChatNameResponse").pyclass

transferFundsIn = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "transferFunds").pyclass

transferFundsOut = GED("http://www.betfair.com/publicapi/v3/BFGlobalService/", "transferFundsResponse").pyclass


# Service Skeletons
class BFGlobalService(ServiceSOAPBinding):
    soapAction = {}
    root = {}

    def __init__(self, post='/BFGlobalService', **kw):
        ServiceSOAPBinding.__init__(self, post)

    def soap_login(self, ps, **kw):
        request = ps.Parse(loginIn.typecode)
        response = betfair_api.login(self, ps, request, loginOut())
        return request,response

    soapAction['login'] = 'soap_login'
    root[(loginIn.typecode.nspname,loginIn.typecode.pname)] = 'soap_login'

    def soap_logout(self, ps, **kw):
        request = ps.Parse(logoutIn.typecode)
        response = betfair_api.logout(self, ps, request, logoutOut())
        return request,response

    soapAction['logout'] = 'soap_logout'
    root[(logoutIn.typecode.nspname,logoutIn.typecode.pname)] = 'soap_logout'

    def soap_getAllEventTypes(self, ps, **kw):
        request = ps.Parse(getAllEventTypesIn.typecode)
        response = betfair_api.getAllEventTypes(self, ps, request, getAllEventTypesOut())
        return request,response

    soapAction['getAllEventTypes'] = 'soap_getAllEventTypes'
    root[(getAllEventTypesIn.typecode.nspname,getAllEventTypesIn.typecode.pname)] = 'soap_getAllEventTypes'

    def soap_getEvents(self, ps, **kw):
        request = ps.Parse(getEventsIn.typecode)
        response = betfair_api.getEvents(self, ps, request, getEventsOut())
        return request, response

    soapAction['getEvents'] = 'soap_getEvents'
    root[(getEventsIn.typecode.nspname,getEventsIn.typecode.pname)] = 'soap_getEvents'



#############################
#    NOT IMPLEMENTED YET    #
#############################

    def soap_keepAlive(self, ps, **kw):
        request = ps.Parse(keepAliveIn.typecode)
        return request,keepAliveOut()

    soapAction['keepAlive'] = 'soap_keepAlive'
    root[(keepAliveIn.typecode.nspname,keepAliveIn.typecode.pname)] = 'soap_keepAlive'

    def soap_retrieveLIMBMessage(self, ps, **kw):
        request = ps.Parse(retrieveLIMBMessageIn.typecode)
        return request,retrieveLIMBMessageOut()

    soapAction['retrieveLIMBMessage'] = 'soap_retrieveLIMBMessage'
    root[(retrieveLIMBMessageIn.typecode.nspname,retrieveLIMBMessageIn.typecode.pname)] = 'soap_retrieveLIMBMessage'

    def soap_submitLIMBMessage(self, ps, **kw):
        request = ps.Parse(submitLIMBMessageIn.typecode)
        return request,submitLIMBMessageOut()

    soapAction['submitLIMBMessage'] = 'soap_submitLIMBMessage'
    root[(submitLIMBMessageIn.typecode.nspname,submitLIMBMessageIn.typecode.pname)] = 'soap_submitLIMBMessage'

    def soap_getActiveEventTypes(self, ps, **kw):
        request = ps.Parse(getActiveEventTypesIn.typecode)
        return request,getActiveEventTypesOut()

    soapAction['getActiveEventTypes'] = 'soap_getActiveEventTypes'
    root[(getActiveEventTypesIn.typecode.nspname,getActiveEventTypesIn.typecode.pname)] = 'soap_getActiveEventTypes'

    def soap_getSubscriptionInfo(self, ps, **kw):
        request = ps.Parse(getSubscriptionInfoIn.typecode)
        return request,getSubscriptionInfoOut()

    soapAction['getSubscriptionInfo'] = 'soap_getSubscriptionInfo'
    root[(getSubscriptionInfoIn.typecode.nspname,getSubscriptionInfoIn.typecode.pname)] = 'soap_getSubscriptionInfo'

    def soap_depositFromPaymentCard(self, ps, **kw):
        request = ps.Parse(depositFromPaymentCardIn.typecode)
        return request,depositFromPaymentCardOut()

    soapAction['depositFromPaymentCard'] = 'soap_depositFromPaymentCard'
    root[(depositFromPaymentCardIn.typecode.nspname,depositFromPaymentCardIn.typecode.pname)] = 'soap_depositFromPaymentCard'

    def soap_addPaymentCard(self, ps, **kw):
        request = ps.Parse(addPaymentCardIn.typecode)
        return request,addPaymentCardOut()

    soapAction['addPaymentCard'] = 'soap_addPaymentCard'
    root[(addPaymentCardIn.typecode.nspname,addPaymentCardIn.typecode.pname)] = 'soap_addPaymentCard'

    def soap_deletePaymentCard(self, ps, **kw):
        request = ps.Parse(deletePaymentCardIn.typecode)
        return request,deletePaymentCardOut()

    soapAction['deletePaymentCard'] = 'soap_deletePaymentCard'
    root[(deletePaymentCardIn.typecode.nspname,deletePaymentCardIn.typecode.pname)] = 'soap_deletePaymentCard'

    def soap_updatePaymentCard(self, ps, **kw):
        request = ps.Parse(updatePaymentCardIn.typecode)
        return request,updatePaymentCardOut()

    soapAction['updatePaymentCard'] = 'soap_updatePaymentCard'
    root[(updatePaymentCardIn.typecode.nspname,updatePaymentCardIn.typecode.pname)] = 'soap_updatePaymentCard'

    def soap_getPaymentCard(self, ps, **kw):
        request = ps.Parse(getPaymentCardIn.typecode)
        return request,getPaymentCardOut()

    soapAction['getPaymentCard'] = 'soap_getPaymentCard'
    root[(getPaymentCardIn.typecode.nspname,getPaymentCardIn.typecode.pname)] = 'soap_getPaymentCard'

    def soap_withdrawToPaymentCard(self, ps, **kw):
        request = ps.Parse(withdrawToPaymentCardIn.typecode)
        return request,withdrawToPaymentCardOut()

    soapAction['withdrawToPaymentCard'] = 'soap_withdrawToPaymentCard'
    root[(withdrawToPaymentCardIn.typecode.nspname,withdrawToPaymentCardIn.typecode.pname)] = 'soap_withdrawToPaymentCard'

    def soap_selfExclude(self, ps, **kw):
        request = ps.Parse(selfExcludeIn.typecode)
        return request,selfExcludeOut()

    soapAction['selfExclude'] = 'soap_selfExclude'
    root[(selfExcludeIn.typecode.nspname,selfExcludeIn.typecode.pname)] = 'soap_selfExclude'

    def soap_convertCurrency(self, ps, **kw):
        request = ps.Parse(convertCurrencyIn.typecode)
        return request,convertCurrencyOut()

    soapAction['convertCurrency'] = 'soap_convertCurrency'
    root[(convertCurrencyIn.typecode.nspname,convertCurrencyIn.typecode.pname)] = 'soap_convertCurrency'

    def soap_getAllCurrencies(self, ps, **kw):
        request = ps.Parse(getAllCurrenciesIn.typecode)
        return request,getAllCurrenciesOut()

    soapAction['getAllCurrencies'] = 'soap_getAllCurrencies'
    root[(getAllCurrenciesIn.typecode.nspname,getAllCurrenciesIn.typecode.pname)] = 'soap_getAllCurrencies'

    def soap_getAllCurrenciesV2(self, ps, **kw):
        request = ps.Parse(getAllCurrenciesV2In.typecode)
        return request,getAllCurrenciesV2Out()

    soapAction['getAllCurrenciesV2'] = 'soap_getAllCurrenciesV2'
    root[(getAllCurrenciesV2In.typecode.nspname,getAllCurrenciesV2In.typecode.pname)] = 'soap_getAllCurrenciesV2'

    def soap_viewReferAndEarn(self, ps, **kw):
        request = ps.Parse(viewReferAndEarnIn.typecode)
        return request,viewReferAndEarnOut()

    soapAction['viewReferAndEarn'] = 'soap_viewReferAndEarn'
    root[(viewReferAndEarnIn.typecode.nspname,viewReferAndEarnIn.typecode.pname)] = 'soap_viewReferAndEarn'

    def soap_viewProfile(self, ps, **kw):
        request = ps.Parse(viewProfileIn.typecode)
        return request,viewProfileOut()

    soapAction['viewProfile'] = 'soap_viewProfile'
    root[(viewProfileIn.typecode.nspname,viewProfileIn.typecode.pname)] = 'soap_viewProfile'

    def soap_viewProfileV2(self, ps, **kw):
        request = ps.Parse(viewProfileV2In.typecode)
        return request,viewProfileV2Out()

    soapAction['viewProfileV2'] = 'soap_viewProfileV2'
    root[(viewProfileV2In.typecode.nspname,viewProfileV2In.typecode.pname)] = 'soap_viewProfileV2'

    def soap_modifyProfile(self, ps, **kw):
        request = ps.Parse(modifyProfileIn.typecode)
        return request,modifyProfileOut()

    soapAction['modifyProfile'] = 'soap_modifyProfile'
    root[(modifyProfileIn.typecode.nspname,modifyProfileIn.typecode.pname)] = 'soap_modifyProfile'


    def soap_withdrawByBankTransfer(self, ps, **kw):
        request = ps.Parse(withdrawByBankTransferIn.typecode)
        return request,withdrawByBankTransferOut()

    soapAction['withdrawByBankTransfer'] = 'soap_withdrawByBankTransfer'
    root[(withdrawByBankTransferIn.typecode.nspname,withdrawByBankTransferIn.typecode.pname)] = 'soap_withdrawByBankTransfer'


    def soap_transferFunds(self, ps, **kw):
        request = ps.Parse(transferFundsIn.typecode)
        return request,transferFundsOut()

    soapAction['transferFunds'] = 'soap_transferFunds'
    root[(transferFundsIn.typecode.nspname,transferFundsIn.typecode.pname)] = 'soap_transferFunds'


####################################
#    UNLIKELY NEED TO BE IMPLEMENTED
####################################

    def soap_createAccount(self, ps, **kw):
        request = ps.Parse(createAccountIn.typecode)
        return request,createAccountOut()

    soapAction['createAccount'] = 'soap_createAccount'
    root[(createAccountIn.typecode.nspname,createAccountIn.typecode.pname)] = 'soap_createAccount'

    def soap_forgotPassword(self, ps, **kw):
        request = ps.Parse(forgotPasswordIn.typecode)
        return request,forgotPasswordOut()

    soapAction['forgotPassword'] = 'soap_forgotPassword'
    root[(forgotPasswordIn.typecode.nspname,forgotPasswordIn.typecode.pname)] = 'soap_forgotPassword'

    def soap_modifyPassword(self, ps, **kw):
        request = ps.Parse(modifyPasswordIn.typecode)
        return request,modifyPasswordOut()

    soapAction['modifyPassword'] = 'soap_modifyPassword'
    root[(modifyPasswordIn.typecode.nspname,modifyPasswordIn.typecode.pname)] = 'soap_modifyPassword'

    def soap_setChatName(self, ps, **kw):
        request = ps.Parse(setChatNameIn.typecode)
        return request,setChatNameOut()

    soapAction['setChatName'] = 'soap_setChatName'
    root[(setChatNameIn.typecode.nspname,setChatNameIn.typecode.pname)] = 'soap_setChatName'