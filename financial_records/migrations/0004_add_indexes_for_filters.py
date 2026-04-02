from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("financial_records", "0003_financialrecord_deleted_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="financialrecord",
            name="type",
            field=models.CharField(
                choices=[("INCOME", "Income"), ("EXPENSE", "Expense")],
                db_index=True,
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="financialrecord",
            name="category",
            field=models.CharField(
                choices=[
                    ("SALARY", "Salary"),
                    ("FREELANCE", "Freelance"),
                    ("INVESTMENT", "Investment"),
                    ("BUSINESS", "Business"),
                    ("RENTAL", "Rental Income"),
                    ("OTHER_INCOME", "Other Income"),
                    ("FOOD", "Food & Dining"),
                    ("TRANSPORT", "Transport"),
                    ("UTILITIES", "Utilities"),
                    ("HEALTH", "Health & Medical"),
                    ("EDUCATION", "Education"),
                    ("ENTERTAINMENT", "Entertainment"),
                    ("SHOPPING", "Shopping"),
                    ("RENT", "Rent"),
                    ("TAX", "Tax"),
                    ("OTHER_EXPENSE", "Other Expense"),
                ],
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="financialrecord",
            name="date",
            field=models.DateField(db_index=True),
        ),
    ]
