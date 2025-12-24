# accounts/models.py
from django.db import models
# accounts/models.py (Append this to the file)

class Account(models.Model):
    ACCOUNT_TYPES = [
        ('ASSET', 'Asset'),
        ('LIABILITY', 'Liability'),
        ('EQUITY', 'Equity'),
        ('REVENUE', 'Revenue'),
        ('EXPENSE', 'Expense'),
    ]

    code = models.CharField(max_length=20, unique=True, help_text="e.g., 1001")
    name = models.CharField(max_length=100, help_text="e.g., Cash on Hand")
    type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class JournalEntry(models.Model):
    date = models.DateField()
    description = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date} - {self.description}"

class JournalItem(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, related_name='items', on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    credit = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.account.name} (Dr: {self.debit} | Cr: {self.credit})"

