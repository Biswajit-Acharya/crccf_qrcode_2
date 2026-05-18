from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "full_name", "designation", "department", "status", "updated_at")
    list_filter = ("status", "department")
    search_fields = ("employee_id", "full_name", "email", "phone")
    readonly_fields = ("created_at", "updated_at", "public_profile_url")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj:
            # Existing QR codes are based on employee_id, so keep it permanent.
            readonly_fields.append("employee_id")
        return readonly_fields

    @admin.display(description="Public QR URL path")
    def public_profile_url(self, obj):
        return obj.get_public_url() if obj and obj.pk else "Saved employee will get a public URL."
