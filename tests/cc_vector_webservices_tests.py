import unittest
from cc_vector_webservices.services.models import Agents
import datetime
from cc_vector_webservices.services.gateway import AgentGateway, CallGateway
import random

class AgentGatewayTest(unittest.TestCase):
    """ Provides function coverage for AgentGateway. """
        
    def setUp(self):        
        self.ANI = '212555555' + str(random.randrange(9))
        self.AgentGateway = AgentGateway()
        self.CallGateway = CallGateway()
        self.today = datetime.datetime.today()
        self.agentToInsert = None
        self.activeAgents = []
        self.activeCalls = []
    def tearDown(self):
        if self.agentToInsert:
            self.agentToInsert.delete()
        if len(self.activeAgents) > 0:
            for agent in self.activeAgents:
                agent.delete()
        if len(self.activeCalls) > 0:
            for call in self.activeCalls:
                call.delete()
    
    def test_registerAgent(self):
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        
        #verify agent was inserted
        
        insertedAgent = Agents.objects.get(ani=self.ANI)
        
        self.assertTrue(insertedAgent)
        self.assertEqual(insertedAgent.ani, self.agentToInsert.ani)
        self.assertEqual(insertedAgent.connection_status, 1)
        self.assertEqual(insertedAgent.phone_status, 0)
        self.assertEqual(insertedAgent.added, self.agentToInsert.added)
        
    def test_getAvailableAgentsByIdleTime(self):
        #insert a bunch of agents
        self.activeAgents.append(self.AgentGateway.registerAgentForServiceToday('2125555560',connection=1,phone=0)) #[0]
        self.activeAgents.append(self.AgentGateway.registerAgentForServiceToday('2125555561',connection=0,phone=0)) #[1]
        self.activeAgents.append(self.AgentGateway.registerAgentForServiceToday('2125555562',connection=1,phone=1)) #[2]
        self.activeAgents.append(self.AgentGateway.registerAgentForServiceToday('2125555563',connection=1,phone=1)) #[3]
        self.activeAgents.append(self.AgentGateway.registerAgentForServiceToday('2125555564',connection=1,phone=0)) #[4]
        self.activeAgents.append(self.AgentGateway.registerAgentForServiceToday('2125555565',connection=1,phone=0)) #[5]
        #insert some calls
        now = datetime.datetime.now()
        self.activeCalls.append(self.CallGateway.addCall(agent=self.activeAgents[0],callEnd=(now + datetime.timedelta(seconds=50)))) #call ended
        self.activeCalls.append(self.CallGateway.addCall(agent=self.activeAgents[2])) #still on call
        self.activeCalls.append(self.CallGateway.addCall(agent=self.activeAgents[3])) #still on call
        self.activeCalls.append(self.CallGateway.addCall(agent=self.activeAgents[4], callEnd=(now + datetime.timedelta(seconds=30)))) #call ended
        self.activeCalls.append(self.CallGateway.addCall(agent=self.activeAgents[5], callEnd=(now + datetime.timedelta(seconds=60)))) #call ended 
        
        #get list of aviable agents
        #this returns unsorted list of hash containing agent ani and idle time
        #should have the following agents: 0,4,5
        avialableAgents = self.AgentGateway.getAvailableAgentsByIdleTime()
        self.assertEqual(len(avialableAgents),3)
         
        
    
    def test_updateAgentPhoneStatus(self):
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        self.assertEqual(self.agentToInsert.ani, self.ANI)
        #default phone status is 0 
        self.assertEqual(self.agentToInsert.phone_status,0)
        
        #change status
        modifiedAgent = self.AgentGateway.updateAgentPhoneStatus(self.agentToInsert,1)
        
        self.assertEqual(modifiedAgent.ani, self.agentToInsert.ani)
        self.assertEqual(modifiedAgent.phone_status, 1)
        
    def test_unregisterAgentForServiceToday(self):
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        #make sure agent is registered for service
        self.assertEqual(self.agentToInsert.ani, self.ANI)
        self.assertEqual(self.agentToInsert.connection_status,1)
        
        #unregister
        unregedAgent = self.AgentGateway.unregisterAgentForServiceToday(self.ANI)
        
        self.assertEqual(self.agentToInsert.ani, unregedAgent.ani)
        self.assertEqual(unregedAgent.connection_status, 0)
        

    def test_isANICurrentlyActive(self):
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        
        self.assertEqual(self.agentToInsert.ani, self.ANI)
        self.assertEqual(self.agentToInsert.connection_status, 1)
        
        self.assertEqual(self.AgentGateway.isANICurrentlyActive(self.ANI), True)


class CallGatewayTest(unittest.TestCase):
    """ Provides function coverage for CallGateway. """
    
    def setUp(self):
        self.AgentGateway = AgentGateway()
        self.CallGateway = CallGateway()
        self.agentToInsert = None
        self.ANI = '212555555' + str(random.randrange(9))
        self.createdCall = None
        self.activeCalls = []
        
    def tearDown(self):
        if self.agentToInsert:
            self.agentToInsert.delete()
        if self.createdCall:
            self.createdCall.delete()
        if len(self.activeCalls) > 0:
            for call in self.activeCalls:
                call.delete()
                
    def test_addCall(self):
        #calls need an agent
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        
        self.createdCall = self.CallGateway.addCall(self.agentToInsert)
        
        self.assertEqual(self.createdCall.agent.ani, self.agentToInsert.ani)
        self.assertNotEqual(self.createdCall.call_start, None)
        
    def test_getLastCallForAgent(self):
        #create some calls for an agent
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        now = datetime.datetime.now()
        self.activeCalls.append(self.CallGateway.addCall(self.agentToInsert, callEnd=(now + datetime.timedelta(seconds=50))))#[0]
        self.activeCalls.append(self.CallGateway.addCall(self.agentToInsert, callEnd=(now + datetime.timedelta(seconds=60))))#[1]
        
        lastCall = self.CallGateway.getLastCallForAgent(self.agentToInsert)
        
        #should return [1]
        self.assertEqual(lastCall.call_id,self.activeCalls[1].call_id)
    
    def test_endCall(self):
        self.agentToInsert = self.AgentGateway.registerAgentForServiceToday(self.ANI)
        self.createdCall = self.CallGateway.addCall(self.agentToInsert)
        
        self.assertEqual(self.createdCall.call_end, None)
        
        #end call
        endedCall = self.CallGateway.endCall(self.createdCall.call_id)
        
        self.assertEqual(self.createdCall.call_id, endedCall.call_id)
        self.assertNotEqual(endedCall.call_end, None)



if __name__ == '__main__':
    unittest.main()