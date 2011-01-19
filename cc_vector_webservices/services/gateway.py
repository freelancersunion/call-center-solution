from cc_vector_webservices.services.models import Agents, CallHistory
from django.db import transaction
import datetime
import logging

log = logging.getLogger("cc_vector_webservices")

class AgentGateway(object):
    """ Gateway to Agent table.
    """    
    
    def updateAgentPhoneStatus(self,agent,phone_status):
        """
        """
        sid = None
        try:
            agent.phone_status = phone_status
            assert(agent.phone_status == phone_status)
            agent.save()
            sid = transaction.savepoint()
            transaction.savepoint_commit(sid)
            return agent
        except Exception as e:
            log.error("services.gateway.updateAgentPhoneStatus: " + e)
            transaction.savepoint_rollback(sid)
            return None
    
    def unregisterAgentForServiceToday(self,ani,connection=0,date=None):
        """
        """
        log.info("in unregisterAgentForServiceToday for agent.ani: " + ani)
        assert(ani)
        today = date or datetime.date.today()        
        sid = None
        try:
            #verify agent is active
            if (self.isANICurrentlyActive(ani)):
                log.info("in unregisterAgentForServiceToday. Agent exists and currently active. About to set as inactive")
                log.info(today.__str__())
                #unregister agent
                agent = Agents.objects.filter(ani=ani, connection_status=1).extra(where=["added between %s and %s"],
                                                                      params=["%s 00:00:00" % (today.__str__()), "%s 24:00:00" % (today.__str__())])[0]
                #set agent as off
                log.info(agent)
                agent.connection_status=0
                log.info("agent connection status:%s ani: %s " % (agent.connection_status,agent.ani))
                assert(agent.connection_status == connection)
                log.info("in unregisterAgentForServiceToday about to save agent")
                agent.save()
                log.info("in unregisterAgentForServiceToday agent saved")
                sid = transaction.savepoint()
                transaction.savepoint_commit(sid)
                return agent
            else:
                #agent was not registered for service
                return None
        except Exception as e:
            log.info("services.gateway.unregisterAgentForServiceToday: " + e)
            transaction.savepoint_rollback(sid)
            return None
    
    def registerAgentForServiceToday(self,ani,connection=1,phone=0,date=None):
        """
        """
        assert(ani)
        today = date or datetime.datetime.today()
        log.info("in registerAgentForServiceToday")
        try:
            agent = Agents(ani=ani, connection_status=connection, phone_status=phone, added=today)
            assert(agent.ani == ani)
            assert(agent.connection_status == connection)
            assert(agent.phone_status == phone)
            assert(agent.added == today)
            log.info("about to call agent.save()")
            agent.save()
            log.info("agent saved")
            sid = transaction.savepoint()
            transaction.savepoint_commit(sid)
            return agent
        except Exception as e:
            log.error("services.gateway.registerAgentForServiceToday: " + e)
            transaction.savepoint_rollback(sid)
            return None
            
    
    def isANICurrentlyActive(self,ani,date=None):
        """ 
        """
        today = date or datetime.date.today()
        ActiveAgents = Agents.objects.filter(ani=ani, connection_status=1).extra(where=["added between %s and %s"],
                                            params=["%s 00:00:00" % (today.__str__()),"%s 24:00:00" % (today.__str__())])
        log.info("Number of active agents with ani: %s is %s" % (ani,len(ActiveAgents)))
        return True if len(ActiveAgents) > 0 else False
    
    def getAvailableAgentsByIdleTime(self,date=None):
        """ Gets avaliable agents by Idle time. 
        Returns a list of dicts with agent and idle time as keys.
        """
        today = date or datetime.date.today()
        availableAgents = Agents.objects.filter(connection_status=1,phone_status=0).extra(where=["added between %s and %s"],
                                                                      params=["%s 00:00:00" % (today.__str__()), "%s 24:00:00" % (today.__str__())])
        #allow agents 120 seconds for post call cleanup
        calls = CallGateway()
        now = datetime.datetime.now()
        availableAgents2 = []       
        for agent in availableAgents:
            log.info("AgentGateway.getAvailableAgentsByIdleTime agent ani: " + agent.ani)
            lastCall = calls.getLastCallForAgent(agent)
            if lastCall is None:
                #this agent just joined, give it the call
                availableAgents2.append({'agent':agent, 'idle': (now - agent.added).seconds})
            else:
                if (now - lastCall.call_end).seconds >= 120:
                    availableAgents2.append({'agent':agent, 'idle': (now-lastCall.call_end).seconds})
                
        return availableAgents2
    
class CallGateway(object):
    """
    """
    
    def addCall(self, agent, callStart=None,callEnd=None):
        """ Adds a call """
        assert(agent)
        sid = None
        callStart = callStart or datetime.datetime.now()
        log.info("in CallGateway.addCall()")
        try:
            if callEnd:
                log.info("in CallGateway.addCall(): call_end provided")
                call = CallHistory(agent=agent, call_start=callStart, call_end=callEnd)
            else:
                log.info("in CallGateway.addCall(): call_end NOT provided")
                call = CallHistory(agent=agent,call_start=callStart )                    
            assert(call.agent.agent_id == agent.agent_id)
            log.info("about to call call.save()")
            call.save()
            log.info("call saved")
            sid = transaction.savepoint()
            transaction.savepoint_commit(sid)
            return call
        except Exception as e:
            log.error("services.gateway.CallGateway.addCall() : " + str(e))
            transaction.savepoint_rollback(sid)
            return None
        
    
    def getLastCallForAgent(self, agentToFind):
        """
        """
        try:
            agentCallHistory = CallHistory.objects.filter(agent=agentToFind).order_by('-call_end')[0]
            return agentCallHistory
        except Exception as e:
            log.error("services.gateway.CallGateway.getLastCallForAgent() : " + str(e))
            return None
        
    def endCall(self,callId,date=None):
        """ """
        #retrieve call from callid
        today = date or datetime.datetime.today()
        sid = None
        try:      
            log.info("in CallGateway.endCall(): about to get call")       
            currentCall = CallHistory.objects.get(call_id=callId)
            log.info("in CallGateway.endCall(): about to set agent phone status to 0")
            agentAssignedToCall = currentCall.agent
            agentAssignedToCall.phone_status=0
            log.info("in CallGateway.endCall(): about to set call end")
            currentCall.call_end = today
            log.info("in CallGateway.endCall(): about to save()")
            currentCall.save()
            agentAssignedToCall.save()
            log.info("in CallGateway.endCall(): call and agent saved")
            sid = transaction.savepoint()
            transaction.savepoint_commit(sid)
            return currentCall
        except Exception as e:
            log.error("services.gateway.CallGateway.endCall() : " + str(e))
            transaction.savepoint_rollback(sid)
            return None
        
        