# accounts/forms.py
from django import forms
from django.forms import inlineformset_factory # Import this
from .models import Account, JournalEntry, JournalItem

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['code', 'name', 'type', 'balance']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control'}),
        }
class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }

class JournalItemForm(forms.ModelForm):
    class Meta:
        model = JournalItem
        fields = ['account', 'debit', 'credit']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'debit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# This creates a "Set" of forms associated with JournalEntry
JournalItemFormSet = inlineformset_factory(
    JournalEntry, 
    JournalItem, 
    form=JournalItemForm,
    extra=2,  # Start with 2 empty rows (standard for double entry)
    can_delete=True
)        