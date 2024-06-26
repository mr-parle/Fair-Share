from django.contrib import admin
from .models import Group, Member, Transaction

admin.site.register(Group)
admin.site.register(Member)
admin.site.register(Transaction)