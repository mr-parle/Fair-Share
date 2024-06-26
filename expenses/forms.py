from django import forms
from .models import Group, Member, Transaction

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['grp_name']

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name']
 
# class TransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ['payer', 'description', 'amount', 'group']
        


#     def __init__(self, group, *args, **kwargs):
#         super(TransactionForm, self).__init__(*args, **kwargs)
#         self.fields['payer'].queryset = group.members.all()
#         self.fields['group'].initial = group   # Set the group field to the current group
#         self.fields['group'].widget = forms.HiddenInput()  # Hide the group field


class TransactionForm(forms.ModelForm):
    def __init__(self, group, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['payer'].queryset = group.members.all()
        self.fields['group'].widget = forms.HiddenInput()
        self.fields['group'].initial = group

    class Meta:
        model = Transaction
        fields = ('payer', 'amount', 'description','group')