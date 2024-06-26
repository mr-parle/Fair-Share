from django.core.management.base import BaseCommand
from expenses.models import Member, Group, GroupMember, Transaction

class Command(BaseCommand):
    help = 'Delete all data from expenses models'

    def handle(self, *args, **kwargs):
        Member.objects.all().delete()
        Group.objects.all().delete()
        GroupMember.objects.all().delete()
        Transaction.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all data from expenses models'))
