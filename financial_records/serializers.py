from rest_framework import serializers
from financial_records.models import FinancialRecord


class FinancialRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialRecord
        fields = [
            "id",
            "amount",
            "type",
            "category",
            "date",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
