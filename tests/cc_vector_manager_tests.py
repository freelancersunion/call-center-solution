import unittest
from cc_vector_manager.call_center_vector import CallCenterVectorConnection,CallCenterVectorPublisher, CallCenterVectorConsumer
import random
import time

class TestConnection(unittest.TestCase):
    """ 
    Units tests for the call center vector connection class 
    """
    
    def setUp(self):
        self.connection_args = {'host':'localhost' ,
                                'port': '5672',
                                'userid':'guest',
                                'password':'ch@ng3m3',
                                'virtual_host':'/',
                                'insist': False,
                                'ssl':False}
 
        self.conn = CallCenterVectorConnection(**self.connection_args)
        
    def tearDown(self):
        self.conn.close()
    
    def test_connection(self):
        assert(self.conn.connection())
        assert(self.conn.channel())

class TestConsumer(unittest.TestCase):
    """ Units tests for the call center vector consumer class.
    """
    
    def setUp(self):
        self.connection_args = {'host':'localhost' ,
                                'port': '5672',
                                'userid':'guest',
                                'password':'ch@ng3m3',
                                'virtual_host':'/',
                                'insist': False,
                                'ssl':False}
        
        self.conn = CallCenterVectorConnection(**self.connection_args)
        self.consumer_args = {'connection':self.conn,
                              'queue': 'test_queue',
                              'queue_durability': True,
                              'queue_exclusivity': False,
                              'queue_auto_delete': False,
                              'exchange' : 'test_exchange',
                              'exchange_type': 'direct',
                              'exchange_durability': True,
                              'exchange_auto_delete': False,
                              'routing_key': 'test_key'                              
                              }
        self.consumer = None
        self.publisher = None

    def tearDown(self):
        self.conn.close()
        if self.consumer:
            self.consumer.close()
        if self.publisher:
            self.publisher.close()
        
    def test_consumer_contructor_with_connection(self):
         #test with connection definied
        self.consumer = CallCenterVectorConsumer(**self.consumer_args)
        self.assertEqual(self.consumer.queue(), self.consumer_args['queue'])
        self.assertEqual(self.consumer.exchange(), self.consumer_args['exchange'])
        self.assertEqual(self.consumer.routingKey(), self.consumer_args['routing_key'])

    def test_consumer_constructor_without_connection(self):
        #test with no connection defined
        self.consumer = CallCenterVectorConsumer(queue=self.consumer_args['queue'], exchange=self.consumer_args['exchange'],
                                                 routing_key=self.consumer_args['routing_key'], exchange_type=self.consumer_args['exchange_type'] )
        self.assertEqual(self.consumer.queue(), self.consumer_args['queue'])
        self.assertEqual(self.consumer.exchange(), self.consumer_args['exchange'])
        self.assertEqual(self.consumer.routingKey(), self.consumer_args['routing_key'])

    def test_basic_get(self):
        #setup publisher and consumer
        publisher = CallCenterVectorPublisher(delivery_mode=2, exchange=self.consumer_args['exchange'], 
                                                   routing_key=self.consumer_args['routing_key'])
        self.consumer = CallCenterVectorConsumer(**self.consumer_args)
        
        #create random message
        sent_message = str(random.randrange(20))
        #publish
        publisher.publish_to_queue(sent_message)
        
        #delay for good faith
        time.sleep(2.5)
        
        #get message and test for integrity 
        recieved_message = self.consumer.basic_get()
        self.assertEqual(sent_message,recieved_message,"MESSAGES DO NOT MATCH: %s %s" % (sent_message,recieved_message))
                
    def test_basic_consume(self):
        """ Its difficult to test this as the message is not returned.
        TODO: Find a way to test this.
        """
        #setup publisher and consumer
#        publisher = CallCenterVectorPublisher(delivery_mode=2, exchange=self.consumer_args['exchange'], 
#                                                   routing_key=self.consumer_args['routing_key'])
#        self.consumer = CallCenterVectorConsumer(**self.consumer_args)
#        
#         #register call back
#        def callback(msg):
#            return msg.body
#        
#        self.consumer.registerCallback(callback)
#        self.consumer.basic_consume(no_ack=True)
#        
#        #create random message
#        sent_message = str(random.randrange(20))
#        #publish
#        publisher.publish_to_queue(sent_message)
#        
#        #delay for good faith
#        time.sleep(2.5)
        pass
        
       
          
        
class TestPublisher(unittest.TestCase):
    """
    Units tests for the call center vector publisher class.
    """
    
    def setUp(self):
        self.connection_args = {'host':'localhost' ,
                                'port': '5672',
                                'userid':'guest',
                                'password':'ch@ng3m3',
                                'virtual_host':'/',
                                'insist': False,
                                'ssl':False}
        
        self.conn = CallCenterVectorConnection(**self.connection_args)
        self.publish_args = {'connection': self.conn,
                             'routing_key': 'test_key',
                             'delivery_mode': 2,
                             'exchange': 'test_exchange'
                             }
        self.consumer_args = {'queue':'test_queue',
                              'exchange' : 'test_exchange',
                              'exchange_type': 'direct',
                              'routing_key': 'test_key'     }
        self.publisher= None
        self.consumer = None
        
        
    def tearDown(self):
        self.conn.close()
        self.publisher.close()
        if self.consumer:
            self.consumer.close()
        
        
    def test_publish_constructor_with_defined_connection(self):
        #test with connection definied
        self.publisher = CallCenterVectorPublisher(**self.publish_args)
        assert(self.publisher.channel())
        assert(self.publisher.delivery_mode())
        assert(self.publisher.connection())
        assert(self.publisher.routing_key())
        
        
    def test_publisher_constructor_without_connection(self):
        self.publisher = CallCenterVectorPublisher(delivery_mode=self.publish_args['delivery_mode'], exchange=self.publish_args['exchange'], 
                                                   routing_key=self.publish_args['routing_key'])
        assert(self.publisher.channel())
        assert(self.publisher.delivery_mode())
        assert(self.publisher.connection())
        assert(self.publisher.routing_key())
        
    
    def test_publish(self):
        self.publisher = CallCenterVectorPublisher(**self.publish_args)
        self.consumer = CallCenterVectorConsumer(**self.consumer_args)
        
        #create random message
        created_message = str(random.randrange(20))
        sent_message = self.publisher.publish_to_queue(created_message)
        self.assertEqual(created_message,sent_message,"The created message and returned message do not match: %s %s" % (created_message, sent_message))
        
        #delay for good faith
        time.sleep(2.5)
        #get message and test for integrity 
        recieved_message = self.consumer.basic_get()
        self.assertEqual(created_message,recieved_message,"MESSAGES DO NOT MATCH: %s %s" % (created_message,recieved_message))
        

        
        
if __name__ == '__main__':
    unittest.main()