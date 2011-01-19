# Create your views here.
import json as simplejson
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings as SETTINGS 
from cc_vector_manager.call_center_vector import CallCenterVectorPublisher
from cc_vector_manager.config import CallMQConfigDev
from cc_vector_webservices.services.gateway import AgentGateway, CallGateway
import logging

log = logging.getLogger('cc_vector_webservices')

def test(request):
    print request.POST
    return HttpResponse("OK") 

def get_static_media(request,static_resource):
    """ retrieves static files. """
    log.info("Recieved request for static file: " + static_resource)
    file = open(SETTINGS.STATIC_ROOT + '/%s' % (static_resource))
    file_text = file.read()
    file.close()
    contentType=None
    #get content type
    if len(static_resource) - static_resource.find('js') == 2:
        #js script
        contentType="text/javascript"
    if len(static_resource) - static_resource.find('jpg') == 3:
        #image
        contentType="image/JPEG"
    return HttpResponse(file_text,content_type=contentType)

def incoming_connection(request):
    """
    Sets up context for incoming connection into call center.
    """
    #TODO: add priority queue
    try:
        assert(request.POST['currentSessionID'])
        assert(request.POST['uniqueIdentifier'])
        #add to vector queue
        log.info("currentSessionID: %s | uniqueID: %s " % (request.POST['currentSessionID'],request.POST['uniqueIdentifier']))
        publisher_args = {CallMQConfigDev.DEFAULT_ROUTING_KEY_KEY: CallMQConfigDev.DEFAULT_ROUTING_KEY_VALUE,
                          CallMQConfigDev.DEFAULT_DELIVERY_MODE_KEY: CallMQConfigDev.DEFAULT_DELIVERY_MODE,
                          CallMQConfigDev.DEFAULT_EXCHANGE_VALUE_KEY: CallMQConfigDev.DEFAULT_EXCHANGE_VALUE
                         }

        
        publisher = CallCenterVectorPublisher(**publisher_args)
        
        #setup message
        msg = simplejson.dumps({'session': request.POST['currentSessionID'] , 'id': request.POST['uniqueIdentifier']})
        log.info("message dumped as json")
        publisher.publish_to_queue(msg)
        log.info("message pushed to queue")
        #return next state and hold dialog
        return HttpResponse("hold.noprompt") 
    except Exception as e:
        log.error("Module: views.incoming_connection. Error: " + e)
        return HttpResponse("incoming_connection.error") 
    
    
def agent_registration(request):
    """ Registers an active agent for the call center. """
    try:
        log.info("retrieved agent ANI:" + request.POST['agentANI'])
        assert(request.POST['agentANI'])        
        agentGateway = AgentGateway()
        #check if agent is already active
        if(agentGateway.isANICurrentlyActive(request.POST['agentANI'])):
            #agent already active
            log.info("agent_registration: agent already active ani: " + request.POST['agentANI'])
            return HttpResponse('registration.agent_already_active')
        else:
            #INSERT INTO DB
            log.info("about to call registerAgentForServiceToday()")
            agentGateway.registerAgentForServiceToday(request.POST['agentANI'])
            log.info("registered agent")      
            return HttpResponse('registration.successful')                
    except Exception as e:
        log.error("Module: views.agent_registration. Error: " + e)
        return HttpResponse('registration.unsuccessful')
    

def agent_client(request):
    """
        Returns a thin client for agents.
    """
    return render_to_response("agent_client.tmpl", {'PHONO_API_KEY': SETTINGS.PHONO_API_KEY})
        
    
def phone_client(request):
    """
      Returns a registration portal for agents using telephones.
    """
    return render_to_response("phone_client.tmpl")

def agent_unregistration(request):
    """ Unregisters an active agent for the call center. """
    log.info("agent_unregistration. retrieved agent ANI:" + request.POST['agentANI'])
    agentGateway = AgentGateway()
    response = agentGateway.unregisterAgentForServiceToday(request.POST['agentANI'])
    if response:
        return HttpResponse('unregistration.successful')    
    else:
        return HttpResponse('unregistration.unsuccessful')


def end_call(request):
    """ Ends a current call.
    """
    log.info("end_call. retrieved request to end call with id: " + request.POST['IVRCallID'])
    callGateway = CallGateway()
    response = callGateway.endCall(request.POST['IVRCallID'])
    if response:
        return HttpResponse('call_end.successful')
    else:
        return HttpResponse('call_end.unsuccessful')