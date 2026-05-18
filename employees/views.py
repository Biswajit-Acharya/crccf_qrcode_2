from io import BytesIO

import qrcode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import FileResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import EmployeeForm
from .models import Employee


def admin_required(view_func):
    @login_required
    @user_passes_test(lambda user: user.is_staff or user.is_superuser)
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped


@admin_required
def dashboard(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    employees = Employee.objects.all()

    if query:
        employees = employees.filter(Q(employee_id__icontains=query) | Q(full_name__icontains=query))

    if status in {Employee.Status.ACTIVE, Employee.Status.INACTIVE}:
        employees = employees.filter(status=status)

    return render(
        request,
        "employees/dashboard.html",
        {"employees": employees, "query": query, "status": status},
    )


@admin_required
def employee_create(request):
    form = EmployeeForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        employee = form.save()
        messages.success(request, f"Employee {employee.employee_id} added successfully.")
        return redirect("dashboard")
    return render(request, "employees/employee_form.html", {"form": form, "title": "Add Employee"})


@admin_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    form = EmployeeForm(request.POST or None, request.FILES or None, instance=employee)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Employee {employee.employee_id} updated successfully.")
        return redirect("dashboard")
    return render(request, "employees/employee_form.html", {"form": form, "title": "Edit Employee"})


@admin_required
@require_http_methods(["GET", "POST"])
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect("dashboard")
    return render(request, "employees/employee_confirm_delete.html", {"employee": employee})


@admin_required
def employee_qr_download(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    qr = qrcode.QRCode(box_size=10, border=4)

    # The QR stores only a permanent public URL, never employee details.
    # In production, set PUBLIC_SITE_URL=https://yourdomain.com so downloaded
    # QR codes always point at the deployed site even behind a proxy.
    public_path = employee.get_public_url()
    site_url = getattr(settings, "PUBLIC_SITE_URL", "").rstrip("/")
    qr_url = f"{site_url}{public_path}" if site_url else request.build_absolute_uri(public_path)
    qr.add_data(qr_url)

    qr.make(fit=True)
    image = qr.make_image(fill_color="#08284a", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    filename = f"{employee.employee_id}_qr.png"

    return FileResponse(buffer, as_attachment=True, filename=filename)


def employee_public(request, employee_id):
    # Public users get read-only access. Every scan queries the live database,
    # so edits made by admin appear through the same old QR URL.
    employee = Employee.objects.filter(employee_id=employee_id, status=Employee.Status.ACTIVE).first()
    return render(
        request,
        "employees/public_employee.html",
        {
            "employee": employee,
            "employee_id": employee_id,
            "not_found_message": "Employee not active or not found.",
        },
    )


def employee_api(request, employee_id):
    # Optional JSON endpoint for the same permanent employee URL identity.
    employee = Employee.objects.filter(employee_id=employee_id, status=Employee.Status.ACTIVE).first()
    if employee is None:
        return JsonResponse({"detail": "Employee not active or not found."}, status=404)

    data = {
        "employee_id": employee.employee_id,
        "full_name": employee.full_name,
        "designation": employee.designation,
        "department": employee.department,
        "phone": employee.phone,
        "email": employee.email,
        "company_name": employee.company_name,
        "company_address": employee.company_address,
        "joining_date": employee.joining_date.isoformat(),
        "status": employee.status,
        "verification_status": "Verified Employee"
        if employee.status == Employee.Status.ACTIVE
        else "Inactive Employee",
        "updated_at": employee.updated_at.isoformat(),
    }
    return JsonResponse(data)
