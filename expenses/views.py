from django.shortcuts import render, redirect, get_object_or_404
from.forms import CreateGroupForm, TransactionForm
from django.http import HttpResponseRedirect
from.models import Group, Member, Transaction, GroupMember
from django.urls import reverse
from collections import defaultdict
from decimal import Decimal
import json

def dashboard(request):
    groups = Group.objects.all()
    return render(request, 'expenses/dashboard.html', {'groups': groups})


def create_group(request):
    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group_name = form.cleaned_data['group_name']
            group = Group.objects.create(grp_name=group_name)
            member_list = request.POST.get('member_list')
            member_list = json.loads(member_list)  # Convert JSON string to list
            for member in member_list:
                member_instance, created = Member.objects.get_or_create(name=member['name'])
                GroupMember.objects.create(group=group, member=member_instance)
            return redirect('group_detail', group_id=group_id)
    else:
        form = CreateGroupForm()
    context = {'form': form}
    return render(request, 'expenses/create.html', context)


def edit_group(request, group_id):
    group = Group.objects.get(id=group_id)
    members = [{'id': member.id, 'username': member.username} for member in group.members.all()]
    return render(request, 'expenses/edit_group.html', {'group': group, 'members': members})



def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    members = group.members.all()
    # print("Members:", members) 
    transactions = Transaction.objects.filter(group=group)
    
    settlements = []
    if transactions.exists():    
        settlements_context = split_expenses(request, group_id)
        settlements = settlements_context.get('settlements', [])
        
    context = {
        'group': group,
        'members': members,
        'transactions': transactions,
        'settlements': settlements
    } 

    return render(request, 'expenses/group_detail.html', context)



def add_transaction(request, group_id):    
    group = get_object_or_404(Group, id=group_id)
    # print(group.members.all())  # Check if this prints any members
    if request.method == 'POST':
        form = TransactionForm(group, request.POST)  # Pass the group object here
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.group = group
            transaction.save()
            members = request.POST.getlist('members')
            for member_id in members:
                member = Member.objects.get(id = member_id)
                transaction.members.add(member)
            return redirect('group_detail', group_id=group_id)  # redirect to transaction list
    else:
        form = TransactionForm(group)  # Pass the group object here
    return render(request, 'expenses/add_transaction.html', {'form': form, 'group': group})

def edit_transaction(request,group_id, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    group = transaction.group
    if request.method == 'POST':
        form = TransactionForm(group, request.POST, instance=transaction)
        if form.is_valid():
            form.save()
            # return redirect('expenses/group_detail.html', group_id=group.id)
            return redirect('group_detail', group_id=group_id)
    else:
        form = TransactionForm(group, instance=transaction)
    return render(request, 'expenses/edit_transaction.html', {'form': form, 'group': group, 'transaction': transaction})
    
def delete_transaction(request, group_id, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    group = transaction.group
    if request.method == 'POST':
        transaction.delete()
        return redirect('group_detail', group_id=group_id)
    return render(request, 'expenses/delete_transaction.html', {'transaction': transaction, 'group': group})
 

def go_back(request):
    referrer = request.META.get('HTTP_REFERER')
    if referrer:
        return HttpResponseRedirect(referrer)
    else:
        return HttpResponseRedirect(reverse('group_detail'))

    
def split_expenses(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    transactions = Transaction.objects.filter(group=group)
    members = group.members.all()

    # Initialize dictionaries to track expenses and payments
    member_expenses = defaultdict(Decimal)
    member_paid = defaultdict(Decimal)

    # Calculate total expenses per member and total amount paid per member
    for transaction in transactions:
        split_between = transaction.group.members.all()
        split_amount = Decimal(transaction.amount) / split_between.count()

        for member in split_between:
            member_expenses[member.id] += Decimal(split_amount)
        
        member_paid[transaction.payer.id] += Decimal(transaction.amount)

    # Calculate net balances (positive for creditors, negative for debtors)
    net_balances = {member.id: member_paid[member.id] - member_expenses[member.id] for member in members}

    # Lists for creditors and debtors
    creditors = sorted([(member.id, net_balances[member.id]) for member in members if net_balances[member.id] > 0], key=lambda x: x[1], reverse=True)
    debtors = sorted([(member.id, net_balances[member.id]) for member in members if net_balances[member.id] < 0], key=lambda x: x[1])

    settlements = []
        # Settling debts
    settlements = []

    # Settling debts
    while creditors and debtors:
        creditor_id, credit_amount = creditors.pop(0)
        debtor_id, debt_amount = debtors.pop(0)

        settle_amount = min(credit_amount, -debt_amount)

        settlements.append({
            'debtor_name': members.get(id=debtor_id).name,
            'creditor_name': members.get(id=creditor_id).name,
            'settle_amount': int(settle_amount)
        })

        if credit_amount > settle_amount:
            creditors.insert(0, (creditor_id, credit_amount - settle_amount))
        if -debt_amount > settle_amount:
            debtors.insert(0, (debtor_id, debt_amount + settle_amount))

    return {'settlements': settlements}


    # # Settling debts
    # while creditors and debtors:
    #     creditor_id, credit_amount = creditors.pop(0)
    #     debtor_id, debt_amount = debtors.pop(0)

    #     settle_amount = min(credit_amount, -debt_amount)

    #     settlements.append(f"{members.get(id=debtor_id).name} → {members.get(id=creditor_id).name} {settle_amount:.2f}")

    #     if credit_amount > settle_amount:
    #         creditors.insert(0, (creditor_id, credit_amount - settle_amount))
    #     if -debt_amount > settle_amount:
    #         debtors.insert(0, (debtor_id, debt_amount + settle_amount))

    # context = {
    #     'settlements': settlements
    # }



# def split_expenses(request, group_id):
#     group = get_object_or_404(Group, id=group_id)
#     transactions = Transaction.objects.filter(group=group)
#     members = group.members.all()

#     # Initialize dictionaries to track expenses and payments
#     member_expenses = defaultdict(float)
#     member_paid = defaultdict(float)

#     # Calculate total expenses per member and total amount paid per member
#     for transaction in transactions:
#         split_between = transaction.group.members.all()
#         split_amount = transaction.amount / split_between.count()

#         for member in split_between:
#             member_expenses[member.id] += split_amount
        
#         member_paid[transaction.payer.id] += transaction.amount

#     # Calculate net balances (positive for creditors, negative for debtors)
#     net_balances = {member.id: member_paid[member.id] - member_expenses[member.id] for member in members}

#     # Lists for creditors and debtors
#     creditors = sorted([(member.id, net_balances[member.id]) for member in members if net_balances[member.id] > 0], key=lambda x: x[1], reverse=True)
#     debtors = sorted([(member.id, net_balances[member.id]) for member in members if net_balances[member.id] < 0], key=lambda x: x[1])

#     settlements = []

#     # Settling debts
#     while creditors and debtors:
#         creditor_id, credit_amount = creditors.pop(0)
#         debtor_id, debt_amount = debtors.pop(0)

#         settle_amount = min(credit_amount, -debt_amount)

#         settlements.append(f"{members.get(id=debtor_id).name} owes {members.get(id=creditor_id).name} ${settle_amount:.2f}")

#         if credit_amount > settle_amount:
#             creditors.insert(0, (creditor_id, credit_amount - settle_amount))
#         if -debt_amount > settle_amount:
#             debtors.insert(0, (debtor_id, debt_amount + settle_amount))

#     context = {
#         'settlements': settlements
#     }

#     return context


    # context = {
    #     'group': group,
    #     'balances': balances,
    # }
    # return render(request, 'expenses/group_details.html', context)
    


# def split_expenses(request, group_id):
#     group = get_object_or_404(Group, id=group_id)
#     context = {}
#     transactions = Transaction.objects.filter(group=group)
#     members = group.members.all()
    
#     balances = {}    
#     # Initialize balances for each member
#     for member in members:
#         balances[member.name] = 0
        
#     # Calculate the total amount paid by each member
#     for transaction in transactions:
#        balances[transaction.payer.name] += transaction.amount
       
#      # Calculate the total amount owed by each member
#     for transaction in transactions:
#        member_count = transaction.members.count()
#        if member_count > 0:
#            split_amount = transaction.amount / member_count
#            for member in transaction.members.all():
#                if member.name == transaction.payer.name:
#                    balances[member.name] += split_amount
#                else:
#                    balances[member.name] -= split_amount
                   
#        else:
#            # Handle the case where there are no members
#            print(f" Warning: Transaction {transaction.id} has no members")
           
#     creditors = {member: balance for member, balance in balances.items() if balance > 0}
#     debtors = {member: -balance for member, balance in balances.items() if balance < 0}
                
#     debtors = sorted(debtors.items(), key=lambda x: x[1], reverse=True)
#     creditors = sorted(creditors.items(), key=lambda x: x[1], reverse=True)
    
#     settlements = []
#     while creditors and debtors:
#        creditor, credit = creditors[0]
#        debtor, debt = debtors[0]
#        if debt >= credit:
#            settlements.append(f"{debtor} → {creditor} {credit:.2f}")
#            debtors[0] = (debtor, debt - credit)
#            if debt - credit == 0:
#                debtors.pop(0)
#            creditors.pop(0)
#        else:
#            settlements.append(f"{debtor} → {creditor} {debt:.2f}")
#            creditors[0] = (creditor, credit - debt)
#            if credit - debt == 0:
#                creditors.pop(0)
#            debtors.pop(0)
#     # for debtor, debt in debtors:
#     #    settlements.append(f"{debtor} owes {debt:.2f}")
#     # for creditor, credit in creditors:
#     #    settlements.append(f"{creditor} is owed {credit:.2f}")
              
#     context['settlements'] = settlements
#     # context['group'] = group
#     return context
# #    return render(request, 'group_detail.html', context)    
     
                
            
            
            
    # context[group.grp_name] = balances
 













# def split_expenses(request, group_id):
#     group = get_object_or_404(Group, id=group_id)
#     context = {}
#     transactions = Transaction.objects.filter(group=group)
#     # print(f"#1 transacti0onsss areee   {transactions}")
#     members = group.members.all()
#     # print(f"#2 members areee   {members}")
    
#     balances = {}
    
#      # Initialize balances for each member
#     # print("loops 1")
#     for member in members:
#         balances[member.name] = 0
#         # print(f" $$$ {balances[member.name]}")
         
         
#     # Calculate the total amount paid by each member
#     # print("loops 2")
#     for transaction in transactions:
#         balances[transaction.payer.name] += transaction.amount
#         # print(f" #3 transaction.payer.name   {transaction.payer.name}") 
#         # print(f"#4 transaction.amount   {transaction.amount}") 
#     # print(f"(#5 balance  {balances}")

#     # Calculate the total amount owed by each member
#     print("loops 3")
#     # for transaction in transactions:
#         # print(f"&&&& each value of the loop 3   {transaction}")
#         member_count = transaction.members.count()
#         # print(f"#6 member_count  {member_count}") 
#         # print(f" #7 transaction.members all  {transaction.members.all()}") 
#         if member_count > 0:
#             # print(f"#$$$$4 transaction.amount   {transaction.amount} by {transaction.payer.name}") 
            
#             split_amount = transaction.amount / member_count
#             for member in transaction.members.all():
#                 if member.name == {transaction.payer.name}:
#                     balances[member.name] += split_amount
#                 else:
#                     balances[member.name] -= split_amount
                    
#                     # print(f"(#8 balance=> member name  {member.name} ---amt:  {balances[member.name]}")
            
#         else:
#             # Handle the case where there are no members
#             print(f" Warning: Transaction {transaction.id} has no members")
        
            

    
    # creditors = {member: balance for member, balance in balances.items() if balance > 0}
    # debtors = {member: -balance for member, balance in balances.items() if balance < 0}

    # creditors = sorted(creditors.items(), key=lambda x: x[1], reverse=True)
    # debtors = sorted(debtors.items(), key=lambda x: x[1], reverse=True)
    
    # while creditors and debtors:
    #     creditor, credit = creditors[0]
    #     debtor, debt = debtors[0]
    #     if debt >= credit:
    #         print(f"{debtor} → {creditor} {credit}")
    #         debtors[0] = (debtor, debt - credit)
    #         creditors.pop(0)
    #     else:
    #         print(f"{debtor} → {creditor} {debt}")
    #         creditors[0] = (creditor, credit - debt)
    #         debtors.pop(0)
    
    













# def split_expenses(request):
#     groups = Group.objects.all()
#     context = {}
    # Calculate the final balances
    # for member in members:
    #     if balances[member.name] > 0:
    #         balances[member.name] = f"{member.name} is owed {balances[member.name]}"
    #         print(f"finalllll {balances[member.name]}")
    #     elif balances[member.name] < 0:
    #         balances[member.name] =  f"{member.name} owes {-balances[member.name]}"
    #         print(f"finalllll   {balances[member.name]}")
    #     else:
    #         balances[member.name] = f"{member.name} is settled"
    #         print(f"{balances[member.name]}")
    
    # for member, balance in balances.items():
    #     if balance > 0:
    #         for other_member, other_balance in balances.items():
    #             if other_balance < 0 and other_member != member:
    #                 print(f"{other_member} → {member} {balance}")
    #                 break
    #     elif balance < 0:
    #         for other_member, other_balance in balances.items():
    #             if other_balance > 0 and other_member != member:
    #                 print(f"{member} → {other_member} {-balance}")
    #                 break
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