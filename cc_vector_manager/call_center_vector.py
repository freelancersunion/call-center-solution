from amqplib import client_0_8 as ampq
from config import CallMQConfigDev as MQConfig
import uuid
import json as simplejson

import logging

log = logging.getLogger('cc_vector_manager')

class CallCenterVectorConnection(object):
    """ Creates a connection to to ampq queues. """
    
         
    def __init__(self, host=MQConfig.DEFAULT_HOST, port=MQConfig.DEFAULT_PORT, userid=MQConfig.DEFAULT_USERID, 
                 password=MQConfig.DEFAULT_PASSWORD, virtual_host=MQConfig.DEFAULT_VHOST, insist=MQConfig.DEFAULT_INSIST, ssl=MQConfig.DEFAULT_SSL):        
        self.__host = host
        self.__port = port
        self.__userid = userid
        self.__password = password
        self.__virtual_host = virtual_host
        self.__insist = insist
        self.__ssl = ssl
        
        try:
            #estabilish a connection
            self.__connection = ampq.Connection(host= '%s:%s' % (self.__host, self.__port),
                                              userid=self.__userid,
                                              password = self.__password,
                                              virtual_host = self.__virtual_host,
                                              ssl = self.__ssl,
                                              insist = self.__insist
                                              )
            #get a channel
            self.__channel = self.__connection.channel()
        except Exception:
            self.__connection = None
    
    def connection(self):
        """ returns MQ connection object. """
        return self.__connection
    
    def channel(self):
        """ returns assigned channel. """
        return self.__channel
        
    def close(self):
        """ Closes channel and connections. """
        self.__channel.close()
        self.__connection.close()
        
class CallCenterVectorPublisher(object):
    """ Class representing a publisher to the call center connection queue. """
    
    def __init__(self, connection=None, routing_key=None, delivery_mode=MQConfig.DEFAULT_DELIVERY_MODE, exchange=None):
        """ Sets up a publisher. """
        
        
        self.__connection = connection or CallCenterVectorConnection()
        self.__routing_key = routing_key
        self.__delivery_mode = delivery_mode
        self.__exchange = exchange
        assert(self.__connection)
        assert(self.__routing_key)
        assert(self.__exchange)
        assert(self.__connection.channel())
        
    def publish_to_queue(self, data):
        """ pushes a message to the queue. """
        msg = ampq.Message(data)
        msg.properties['delivery_mode'] = self.__delivery_mode
        self.__connection.channel().basic_publish(msg,
                                   exchange=self.__exchange,
                                   routing_key=self.__routing_key)
        return msg.body
    
    def close(self):
        """ closes the connection. """
        self.__connection.close()
    
    def connection(self):
        """ returns the connection object. """
        return self.__connection
    
    def routing_key(self):
        """ returns a string representing the routing key specified. """
        return self.__routing_key
    
    def delivery_mode(self):
        """ returns a string specifing the delivery mode. """
        return self.__delivery_mode
    
    def channel(self):
        """ returns the current channel assigned to the connection. """
        return self.__connection.channel()
    
class CallCenterVectorConsumer(object):
    """ Sets up a consumer. """
    
    def __init__(self, connection=None, queue=None, queue_durability=True, queue_exclusivity=False, queue_auto_delete=False,
                 exchange=None, exchange_type=None, exchange_durability=True, exchange_auto_delete=False, routing_key=None):
        """Constructor.
        connection: A CallCenterVectorConnection() instance
        queue: name of queue to be created or attached to
        queue_durablity: ensure the queue will be re-created on server reboot
        queue_auto_delete: Flag that controls whether queue will be automaticly deleted when the last consumer detaches
        queue_exclusivity: Flag that sets the creating consumer as the only consumer allowed to attach to queue. 
        exchange: name of exchange to be created or attached to
        exchange_type: type of exchange (fanout, direct, topic)
        exchange_durabilty: ensure the exchange will be recreated on server reboot
        exchange_auto_delete: Flag that controls whether exchange will be automaticlly deleted when the last consumer detaches
        """
        self.__connection = connection or CallCenterVectorConnection()
        self.__queue = queue
        self.__queue_durabilty = queue_durability
        self.__queue_exclusivity = queue_exclusivity
        self.__queue_auto_delete = queue_auto_delete
        self.__exchange = exchange
        self.__exchange_type = exchange_type
        self.__exchange_durabilty = exchange_durability
        self.__exchange_auto_delete = exchange_auto_delete 
        self.__routing_key = routing_key
        self.__callback = None
        self.WAIT = True
        self.__consumer_tag = uuid.uuid4().__str__() 
        
        assert(self.__connection)
        assert(self.__queue)
        assert(self.__exchange)
        assert(self.__exchange_type)
        assert(self.__routing_key)
        
        self.queue_declare()
        self.exchange_declare()
        self.queue_bind()
        
    def queue_declare(self):
        #create queue
        self.__connection.channel().queue_declare(queue=self.__queue,
                                                durable=self.__queue_durabilty,
                                                exclusive=self.__queue_exclusivity,
                                                auto_delete=self.__queue_auto_delete)
        
    def exchange_declare(self): 
        #create exchange
        self.__connection.channel().exchange_declare(exchange=self.__exchange,
                                                   type=self.__exchange_type,
                                                   durable=self.__exchange_durabilty,
                                                   auto_delete=self.__exchange_auto_delete)
        
    def queue_bind(self):
        #bind queue to exchange
        self.__connection.channel().queue_bind(queue=self.__queue,
                                             exchange=self.__exchange,
                                             routing_key=self.__routing_key)
        
    def basic_consume(self, no_ack=False):
        self.__connection.channel().basic_consume(queue=self.__queue,
                                                no_ack = no_ack,
                                                callback=self.__call_back,
                                                consumer_tag=self.__consumer_tag
                                                )
    def wait(self):
        while self.WAIT:
            self.__connection.channel().wait()                
    
    def endWait(self):
        self.WAIT = False
        
    def queue(self):
        return self.__queue
    
    def exchange(self):
        return self.__exchange
    
    def routingKey(self):
        return self.__routing_key     

    def close(self):
        self.__connection.close()
        
    def registerCallback(self, callback):
        """ registers a tag to a specific callback. """
        self.__call_back = callback
    
    def basic_get(self):
        msg = self.__connection.channel().basic_get(self.__queue)
        if (msg):
           self.__connection.channel().basic_ack(msg.delivery_tag)
        return msg.body

    
        
class CallCenterVectorManager(object):
    """ Handles selection of agents based on different routing algorithms.
        Currently implementing UCD-MIA.
    """
    
    
    def __init__(self):
        from cc_vector_manager.routing_algorithms import UCD_MIA_Alogrithm
        from cc_vector_webservices.services.gateway import AgentGateway, CallGateway
        self.algo = UCD_MIA_Alogrithm()
        #create gateway instances     
        self.agentGateway = AgentGateway()
        self.callGateway = CallGateway()
        
    def getNextAgent(self,msg):
        from urllib import urlencode
        from urllib2 import urlopen, Request
        from config import IVRSettings as SETTINGS
        #get next available agent 
        log.info("in CallCenterVectorManager.getNextAgent()")
        #get message contents
        loadedMessage = simplejson.loads(msg.body)
        ccxmlSessionID = loadedMessage['session']
        ccxmlUniqueID = loadedMessage['id']              
        
        #get available agents
        #returns <Agent Instance>
        agents = self.agentGateway.getAvailableAgentsByIdleTime()
        
        #use our selected UCD_MIA algorithm to select the next agent
        agentWithMostIdleTime = self.algo.getNextAgent(agents)
        
        if agentWithMostIdleTime:            
            #create call with agent
            call = self.callGateway.addCall(agent=agentWithMostIdleTime)
            #update agent phone status
            agentWithMostIdleTime=self.agentGateway.updateAgentPhoneStatus(agentWithMostIdleTime,1)
            #inject event into ccxml session
            data = urlencode({SETTINGS.IVR_SESSION_KEY:ccxmlSessionID, SETTINGS.IVR_EVENT_KEY:SETTINGS.IVR_EVENT_VALUE, \
                              SETTINGS.IVR_UNIQUE_ID_KEY:ccxmlUniqueID, SETTINGS.IVR_AGENT_ANI_KEY:agentWithMostIdleTime.ani, \
                              SETTINGS.IVR_DESTINATION_TYPE_KEY: agentWithMostIdleTime.determineANIType(), \
                              SETTINGS.IVR_CALL_ID_KEY: call.call_id})
            url = SETTINGS.IVR_URL
            request = Request(url, data)
            log.info("ccxml url: " + request.get_full_url() + request.get_data())
            response = urlopen(request)
            if response:
                log.info("Agent assigned to call sucessfully")
            else:
                log.info("Agent assigned to call unsucessfully")
        else:
            #No agent was found
            #send call back to queue
            publisher_args = {MQConfig.DEFAULT_ROUTING_KEY_KEY: MQConfig.DEFAULT_ROUTING_KEY_VALUE,
                          MQConfig.DEFAULT_DELIVERY_MODE_KEY: MQConfig.DEFAULT_DELIVERY_MODE,
                          MQConfig.DEFAULT_EXCHANGE_VALUE_KEY: MQConfig.DEFAULT_EXCHANGE_VALUE
                         }        
            publisher = CallCenterVectorPublisher(**publisher_args)
        
            #setup message
            msg = simplejson.dumps({'session': ccxmlSessionID , 'id': ccxmlUniqueID})
            log.info("message dumped as json")
            publisher.publish_to_queue(msg)
            log.info("message pushed to queue")
            publisher.close()       
       


