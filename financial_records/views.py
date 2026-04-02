from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.tokenauth import TokenAuthentication
from financial_records.models import FinancialRecord
from financial_records.pagination import RecordPagination
from accounts.permissions import IsAdmin, IsAnalyst, IsViewer
from financial_records.serializers import FinancialRecordSerializer


class FinancialRecordListCreateView(APIView):
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdmin()]
        return [IsViewer()]

    def get(self, request):
        records = FinancialRecord.objects.all()

        if request.user.role in ("ANALYST", "ADMIN"):
            type_filter = request.query_params.get("type")
            category_filter = request.query_params.get("category")
            date_from = request.query_params.get("date_from")
            date_to = request.query_params.get("date_to")
            date_exact = request.query_params.get("date")
            search = request.query_params.get("search")

            if type_filter:
                records = records.filter(type=type_filter.upper())
            if category_filter:
                records = records.filter(category__icontains=category_filter)
            if date_exact:
                records = records.filter(date=date_exact)
            else:
                if date_from:
                    records = records.filter(date__gte=date_from)
                if date_to:
                    records = records.filter(date__lte=date_to)
            if search:
                records = records.filter(notes__icontains=search)

        paginator = RecordPagination()
        paginated = paginator.paginate_queryset(records, request)
        serializer = FinancialRecordSerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = FinancialRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "record": serializer.data,
                    "message": "Record created successfully.",
                    "success": True,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FinancialRecordDetailView(APIView):
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAnalyst()]
        return [IsAdmin()]

    def get_object(self, pk):
        try:
            return FinancialRecord.objects.get(pk=pk)
        except FinancialRecord.DoesNotExist:
            return None

    def get(self, request, pk):
        record = self.get_object(pk)
        if record is None:
            return Response(
                {"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = FinancialRecordSerializer(record)
        return Response({"record": serializer.data, "success": True})

    def patch(self, request, pk):
        record = self.get_object(pk)
        if record is None:
            return Response(
                {"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = FinancialRecordSerializer(record, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "record": serializer.data,
                    "message": "Record updated successfully.",
                    "success": True,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        record = self.get_object(pk)
        if record is None:
            return Response(
                {"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND
            )
        record.delete()
        return Response(
            {"message": "Record deleted successfully.", "success": True},
            status=status.HTTP_200_OK,
        )
