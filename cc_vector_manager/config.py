class CallMQConfigDev(object):
        
    DEFAULT_HOST = ''
    DEFAULT_PORT = ''
    DEFAULT_USERID = ''
    DEFAULT_PASSWORD = ''
    DEFAULT_VHOST = '/'
    DEFAULT_INSIST = False
    DEFAULT_SSL = False
    DEFAULT_DELIVERY_MODE_KEY = "delivery_mode"
    DEFAULT_DELIVERY_MODE = 2  #allows for message persistance
    DEFAULT_ROUTING_KEY_KEY = "routing_key"
    DEFAULT_ROUTING_KEY_VALUE = ""
    DEFAULT_EXCHANGE_TYPE_KEY = "exchange_type"
    DEFAULT_EXCHANGE_TYPE_VALUE = ""
    DEFAULT_EXCHANGE_VALUE_KEY = "exchange"
    DEFAULT_EXCHANGE_VALUE = ""
    DEFAULT_QUEUE_KEY = "queue"
    DEFAULT_QUEUE_VALUE = ""
    
    
class IVRSettings(object):
    
############################################################
# IVR CONSTANTS....could probably put these somewhere else #
############################################################
    IVR_URL = "http://session.voxeo.net/CCXML.send?"
    IVR_SESSION_KEY = "sessionid"
    IVR_EVENT_KEY = "eventname"
    IVR_EVENT_VALUE = "agent.retrieved"
    IVR_UNIQUE_ID_KEY = "sentUID"
    IVR_AGENT_ANI_KEY = "availableAgentANI"
    IVR_DESTINATION_TYPE_KEY = "destinationType"
    IVR_CALL_ID_KEY = "callId"