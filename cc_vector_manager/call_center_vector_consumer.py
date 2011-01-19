from cc_vector_manager.call_center_vector import CallCenterVectorConsumer, CallCenterVectorManager
from cc_vector_manager.config import CallMQConfigDev
import logging

log = logging.getLogger('cc_vector_webservices')

def run_consumer():
    """
    """
    #set up consumer
    log.info("...Starting call center vector consumer...")
    consumer_args = {CallMQConfigDev.DEFAULT_QUEUE_KEY:CallMQConfigDev.DEFAULT_QUEUE_VALUE,
                     CallMQConfigDev.DEFAULT_EXCHANGE_VALUE_KEY:CallMQConfigDev.DEFAULT_EXCHANGE_VALUE,
                     CallMQConfigDev.DEFAULT_EXCHANGE_TYPE_KEY:CallMQConfigDev.DEFAULT_EXCHANGE_TYPE_VALUE,
                     CallMQConfigDev.DEFAULT_ROUTING_KEY_KEY:CallMQConfigDev.DEFAULT_ROUTING_KEY_VALUE}
    routingAlgorithm = CallCenterVectorManager()
    vectorConsumer = CallCenterVectorConsumer(**consumer_args)

    vectorConsumer.registerCallback(routingAlgorithm.getNextAgent)
    vectorConsumer.basic_consume(no_ack=True)
   
    log.info("...Waiting for incoming call....")
    vectorConsumer.wait()


if __name__ == '__main__':
    try:
        run_consumer()
    except KeyboardInterrupt as e:
        log.info("....Exiting Consumer Script ......")
        