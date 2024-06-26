from django.shortcuts import render, redirect, get_object_or_404
from.forms import GroupForm, MemberForm, TransactionForm
from.models import Group, Member, Transaction
from django.urls import reverse

def create_group(request):
    if request.method == 'POST':
        group_form = GroupForm(request.POST)
        if group_form.is_valid():
            group = group_form.save()
            members = request.POST.get('members').split(',')
            for member in members:
                member = member.strip()
                if member:
                    member_obj, created = Member.objects.get_or_create(name=member)
                    group.members.add(member_obj)
            return redirect('group_list')  # redirect to a list of groups
    else:
        group_form = GroupForm()
    return render(request, 'create_group.html', {'group_form': group_form})

def create_group(request, group_id):
    
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()  # Get the created group instance
            return redirect('add_member', group_id=group.id)
        
    else:
        form = GroupForm()
    context = { 'form': form, 'members': members , 'groups': groups}
    return render(request, 'expenses/create_group.html', context)

def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()
    print("Members:", members) 
    transactions = Transaction.objects.filter(group=group)
    
    context = {
        'group': group,
        'members': members,
        'transactions': transactions,
    }
    return render(request, 'expenses/group_detail.html', context)

def dashboard(request):
    groups = Group.objects.all()
    valid_groups = [group for group in groups if group.pk is not None]
    logger.info("Groups retrieved: %s", valid_groups)
    return render(request, 'expenses/dashboard.html', {'groups': valid_groups})

def dashboard(request):
    groups = Group.objects.all()
    return render(request, 'expenses/dashboard.html', {'groups': groups})



def add_member(request, group_id):
    
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            # return redirect(reverse('add_member', args=[group_id]))
            return redirect(reverse('add_member', args=[group_id]))
    else:
        form = MemberForm()
    context={'form': form, 'group': group}
    return render(request, 'expenses/add_member.html', context )


def add_transaction(request, group_id):
    
    
    group = get_object_or_404(Group, id=group_id)
    print(group.members.all())  # Check if this prints any members
    if request.method == 'POST':
        form = TransactionForm(group, request.POST)  # Pass the group object here
        if form.is_valid():
            form.save()
            return redirect('transaction_list', group_id=group_id)  # redirect to transaction list
    else:
        form = TransactionForm(group)  # Pass the group object here
    return render(request, 'expenses/add_transaction.html', {'form': form, 'group': group})
    

    
def transaction_list(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    transactions = Transaction.objects.filter(group=group)
    return render(request, 'expenses/transaction_list.html', {'transactions': transactions})

def some_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)


def split_expenses(request, pk):
    group = get_object_or_404(Group, id=pk)
    context = {}
    transactions = Transaction.objects.filter(group=group)
    members = group.members.all()
    total_expense = sum(transaction.amount for transaction in transactions)
    num_members = members.count()

    if num_members == 0:
        return redirect('group_list')  # Skip if there are no members in the group

    split_amount = total_expense / num_members

    balances = {}
    for member in members:
        paid_amount = sum(transaction.amount for transaction in member.payments.all())
        member_share = sum(transaction.amount for transaction in transactions.filter(payer=member))
        balances[member.name] = paid_amount - member_share + split_amount

    context[group.grp_name] = balances
    return render(request, 'expenses/split_expenses.html', {'context': context})




























# def split_expenses(request):
#     groups = Group.objects.all()
#     context = {}
#     for group in groups:
#         transactions = Transaction.objects.filter(group=group)
#         members = Member.objects.filter(group=group)
#         total_expense = sum(transaction.amount for transaction in transactions)
#         split_amount = total_expense / len(members)
        
#         balances = {}
#         for member in members:
#             paid_amount = sum(transaction.amount for transaction in member.payments.all())
#             balances[member.name] = paid_amount - split_amount

#         context[group.name] = balances

#     return render(request, 'expenses/split_expenses.html', {'context': context})


# import logging

# logger = logging.getLogger(__name__)
# def group_detail(request, pk):
#     logger.info("Fetching group with pk: %s", pk)
#     group = get_object_or_404(Group, pk=pk)
#     members = group.get_members()
#     logger.info("Members of group %s: %s", group, members)

#     if request.method == 'POST':
#         member_name = request.POST.get('member_name')
#         logger.info("Received member_name: %s", member_name)
#         if member_name:
#             group.add_member(member_name)
#             logger.info("Added member %s to group %s", member_name, group)
#             return redirect('group_detail', pk=group.pk)

#     context = {'group': group, 'members': members, 'group_id': group.pk}
#     return render(request, 'expenses/group_detail.html', context)