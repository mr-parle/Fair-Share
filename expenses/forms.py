from django import forms
from .models import Group, Member, Transaction

class CreateGroupForm(forms.Form):
    group_name = forms.CharField(max_length=255)
    members = forms.CharField( required=False)
    

    def clean_members(self):
        members = self.cleaned_data['members'].split(',')
        return [member.strip() for member in members]
    
    
    
    
class TransactionForm(forms.ModelForm):
    def __init__(self, group, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['payer'].queryset = group.members.all()
        self.fields['group'].widget = forms.HiddenInput()
        self.fields['group'].initial = group

    class Meta:
        model = Transaction
        fields = ('payer', 'amount', 'description','group')
 
 
 
 
 
 
 
 
 
 
 
 
 
 
# class GroupForm(forms.ModelForm):
#     grp_name = forms.CharField(label='Group Name')
#     class Meta:
#         model = Group
#         fields = ['grp_name']

# class MemberForm(forms.ModelForm):
#     name = forms.CharField(label='Member Name')
#     class Meta:
#         model = Member
#         fields = ['name']
 
 
 