from operator import itemgetter
import logging
import time

log = logging.getLogger('cc_vector_webservices')

class UCD_MIA_Alogrithm(object):
     
    def getNextAgent(self, agents):
        """ Returns the agent with the most idle time. Idle time in seconds. """
        try:            
            #sort agents based on idle time
            agentWithMostIdleTime = sorted(agents, key=itemgetter('idle'),reverse=True)[0]
            log.info("UCD_MIA_Alogrithm.getNextAgent() agentWithMostIdleTime:" + str(agentWithMostIdleTime))
            return agentWithMostIdleTime['agent']
        except IndexError as e:
            #no agents were avialable at this time
            #sleep to reduce cpu strain 
            time.sleep(1)
            log.info("No agent available : " + str(e))
            return None                 
        except Exception as e:
            #unexpected exception
            log.info("UCD_MIA_Alogrithm.getNextAgent() Exception : " + str(e))
            return None     
