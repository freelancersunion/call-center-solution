from django.db import models

class Agents(models.Model):
    agent_id = models.AutoField(primary_key=True)
    ani = models.TextField(unique=True)
    connection_status = models.IntegerField()
    phone_status = models.IntegerField()
    added = models.DateTimeField()
    class Meta:
        db_table = u'agents'
        
    def determineANIType(self):
        """Determines if the ANI is SIP or TEL"""
        if self.ani.find("@") > 0:
            return "SIP"
        else:
            return "TEL"
        
        
class CallHistory(models.Model):
    call_id = models.AutoField(primary_key=True)
    call_start = models.DateTimeField()
    call_end = models.DateTimeField()
    agent = models.ForeignKey(Agents)
    class Meta:
        db_table = u'call_history'
