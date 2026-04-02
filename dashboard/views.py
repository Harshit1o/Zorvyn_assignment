from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from rest_framework.views import APIView
from accounts.permissions import IsViewer
from rest_framework.response import Response
from accounts.tokenauth import TokenAuthentication
from financial_records.models import FinancialRecord
from django.db.models.functions import TruncMonth, TruncWeek


class DashboardSummaryView(APIView):
    permission_classes = [IsViewer]
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        records = FinancialRecord.objects.all()

        # --- Totals ---
        total_income = (
            records.filter(type="INCOME").aggregate(total=Sum("amount"))["total"] or 0
        )

        total_expense = (
            records.filter(type="EXPENSE").aggregate(total=Sum("amount"))["total"] or 0
        )

        net_balance = total_income - total_expense

        # --- Category-wise totals ---
        category_totals = (
            records.values("category", "type")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("type", "-total")
        )

        # --- Recent activity (last 10 records) ---
        recent_records = records.order_by("-date", "-created_at")[:10].values(
            "id", "amount", "type", "category", "date", "notes"
        )

        # --- Monthly trends (last 6 months) ---
        six_months_ago = timezone.now().date().replace(day=1) - timedelta(days=180)
        monthly_trends = (
            records.filter(date__gte=six_months_ago)
            .annotate(month=TruncMonth("date"))
            .values("month", "type")
            .annotate(total=Sum("amount"))
            .order_by("month", "type")
        )

        monthly_data = {}
        for entry in monthly_trends:
            month_str = entry["month"].strftime("%Y-%m")
            if month_str not in monthly_data:
                monthly_data[month_str] = {"income": 0, "expense": 0}
            if entry["type"] == "INCOME":
                monthly_data[month_str]["income"] = float(entry["total"])
            else:
                monthly_data[month_str]["expense"] = float(entry["total"])

        # --- Weekly trends (last 4 weeks) ---
        four_weeks_ago = timezone.now().date() - timedelta(weeks=4)
        weekly_trends = (
            records.filter(date__gte=four_weeks_ago)
            .annotate(week=TruncWeek("date"))
            .values("week", "type")
            .annotate(total=Sum("amount"))
            .order_by("week", "type")
        )

        weekly_data = {}
        for entry in weekly_trends:
            week_str = entry["week"].strftime("%Y-%m-%d")
            if week_str not in weekly_data:
                weekly_data[week_str] = {"income": 0, "expense": 0}
            if entry["type"] == "INCOME":
                weekly_data[week_str]["income"] = float(entry["total"])
            else:
                weekly_data[week_str]["expense"] = float(entry["total"])

        return Response(
            {
                "summary": {
                    "total_income": float(total_income),
                    "total_expense": float(total_expense),
                    "net_balance": float(net_balance),
                },
                "category_totals": list(category_totals),
                "recent_activity": list(recent_records),
                "monthly_trends": [
                    {"month": k, **v} for k, v in sorted(monthly_data.items())
                ],
                "weekly_trends": [
                    {"week_starting": k, **v} for k, v in sorted(weekly_data.items())
                ],
                "success": True,
            }
        )
