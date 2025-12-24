# accounts/views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Account
from .forms import AccountForm
# accounts/views.py (Add imports and the new view)
from django.db import transaction
from django.shortcuts import render, redirect
from .models import Account, JournalEntry
from .forms import AccountForm, JournalEntryForm, JournalItemFormSet
from django.db.models import Sum

# READ (List)
class AccountListView(ListView):
    model = Account
    template_name = 'accounts/account_list.html'
    context_object_name = 'accounts'

# CREATE
class AccountCreateView(CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('account_list')

# UPDATE
class AccountUpdateView(UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'accounts/account_form.html'
    success_url = reverse_lazy('account_list')

# DELETE
class AccountDeleteView(DeleteView):
    model = Account
    template_name = 'accounts/account_confirm_delete.html'
    success_url = reverse_lazy('account_list')


# ... keep existing Account views ...

# NEW: Journal Entry List
class JournalEntryListView(ListView):
    model = JournalEntry
    template_name = 'accounts/journal_list.html'
    context_object_name = 'entries'
    ordering = ['-date']

# NEW: Create Journal Entry
class JournalEntryCreateView(CreateView):
    model = JournalEntry
    form_class = JournalEntryForm
    template_name = 'accounts/journal_form.html'
    success_url = reverse_lazy('journal_list')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['items'] = JournalItemFormSet(self.request.POST)
        else:
            data['items'] = JournalItemFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['items']
        
        if items.is_valid():
            # 1. Custom Validation: Check if Dr == Cr
            total_dr = 0
            total_cr = 0
            for form_item in items:
                if form_item.cleaned_data and not form_item.cleaned_data.get('DELETE', False):
                    total_dr += form_item.cleaned_data.get('debit', 0)
                    total_cr += form_item.cleaned_data.get('credit', 0)
            
            if total_dr != total_cr:
                form.add_error(None, f"Unbalanced Entry! Debits (${total_dr}) must equal Credits (${total_cr})")
                return self.render_to_response(self.get_context_data(form=form))

            # 2. Save everything safely using a transaction
            with transaction.atomic():
                self.object = form.save() # Save Parent (Entry)
                items.instance = self.object # Link Items to Parent
                items.save() # Save Children (Items)
                
                # 3. Update Account Balances (Simple implementation)
                # Note: In a real robust system, balances are calculated on the fly, 
                # but for this tutorial, we update the account field.
                for item in self.object.items.all():
                    acct = item.account
                    # Logic: Asset/Exp increase with Debit. Liab/Eq/Rev increase with Credit.
                    if acct.type in ['ASSET', 'EXPENSE']:
                        acct.balance += (item.debit - item.credit)
                    else:
                        acct.balance += (item.credit - item.debit)
                    acct.save()
                    
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))    

def trial_balance(request):
    accounts = Account.objects.all().order_by('code')
    
    total_dr = 0
    total_cr = 0
    
    # Organize data for the template
    account_list = []
    for acct in accounts:
        dr = 0
        cr = 0
        # Determine which column the balance belongs to based on Account Type
        if acct.type in ['ASSET', 'EXPENSE']:
            dr = acct.balance
            total_dr += dr
        else:
            cr = acct.balance
            total_cr += cr
            
        account_list.append({
            'code': acct.code,
            'name': acct.name,
            'debit': dr,
            'credit': cr
        })

    context = {
        'accounts': account_list,
        'total_dr': total_dr,
        'total_cr': total_cr,
    }
    return render(request, 'accounts/trial_balance.html', context)


# accounts/views.py

def general_ledger(request):
    # 1. Get the list of all accounts for the Dropdown menu
    all_accounts = Account.objects.all().order_by('code')

    # 2. Check if the user selected a specific account
    selected_account_id = request.GET.get('account')

    # 3. Prepare the QuerySet
    # We start with ALL accounts by default
    ledger_data = Account.objects.prefetch_related('journalitem_set__journal_entry').order_by('code')

    # 4. If a specific account is selected, filter the QuerySet
    if selected_account_id:
        ledger_data = ledger_data.filter(id=selected_account_id)

    context = {
        'accounts': ledger_data,         # The accounts to display (Filtered)
        'all_accounts': all_accounts,    # The accounts for the <select> options
        'selected_account_id': int(selected_account_id) if selected_account_id else None
    }
    
    return render(request, 'accounts/general_ledger.html', context)   