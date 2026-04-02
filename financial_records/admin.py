from django.contrib import admin
from financial_records.models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
	list_display = [
		"id",
		"date",
		"type",
		"category",
		"amount",
		"is_deleted",
		"created_at",
	]
	list_filter = ["type", "category", "is_deleted", "date", "created_at"]
	search_fields = ["id", "notes", "category"]
	ordering = ["-date", "-created_at"]
	readonly_fields = ["id", "created_at", "updated_at", "deleted_at"]
	date_hierarchy = "date"

	# Show all rows (including soft-deleted records) in admin.
	def get_queryset(self, request):
		return FinancialRecord.all_objects.all()
