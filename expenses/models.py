
from django.db import models
import uuid

class Member(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grp_name = models.CharField(max_length=25)
    members = models.ManyToManyField(Member, through='GroupMember', related_name='groups')

    def __str__(self):
        return self.grp_name

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.member.name} in {self.group.grp_name}"
    
class Transaction(models.Model):
    payer = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    members = models.ManyToManyField(Member, related_name='transactions')
    

    def __str__(self):
        return f"{self.payer.name} paid {self.amount} for {self.description}"

    def get_group_members(self):
        return self.group.members.all()
