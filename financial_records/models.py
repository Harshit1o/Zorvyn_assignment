import uuid
from django.db import models
from django.utils import timezone


class ActiveRecordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class FinancialRecord(models.Model):
    class Type(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    class Category(models.TextChoices):
        # Income categories
        SALARY = "SALARY", "Salary"
        FREELANCE = "FREELANCE", "Freelance"
        INVESTMENT = "INVESTMENT", "Investment"
        BUSINESS = "BUSINESS", "Business"
        RENTAL = "RENTAL", "Rental Income"
        OTHER_INCOME = "OTHER_INCOME", "Other Income"
        # Expense categories
        FOOD = "FOOD", "Food & Dining"
        TRANSPORT = "TRANSPORT", "Transport"
        UTILITIES = "UTILITIES", "Utilities"
        HEALTH = "HEALTH", "Health & Medical"
        EDUCATION = "EDUCATION", "Education"
        ENTERTAINMENT = "ENTERTAINMENT", "Entertainment"
        SHOPPING = "SHOPPING", "Shopping"
        RENT = "RENT", "Rent"
        TAX = "TAX", "Tax"
        OTHER_EXPENSE = "OTHER_EXPENSE", "Other Expense"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=Type.choices, db_index=True)
    category = models.CharField(max_length=20, choices=Category.choices, db_index=True)
    date = models.DateField(db_index=True)
    notes = models.TextField(blank=True, default="")
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveRecordManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "financial_record"
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.type} | {self.category} | {self.amount}"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
