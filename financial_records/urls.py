from django.urls import path
from financial_records.views import (
    FinancialRecordDetailView,
    FinancialRecordListCreateView,
)

urlpatterns = [
    path(
        "records/", FinancialRecordListCreateView.as_view(), name="record-list-create"
    ),
    path(
        "records/<uuid:pk>/", FinancialRecordDetailView.as_view(), name="record-detail"
    ),
]
