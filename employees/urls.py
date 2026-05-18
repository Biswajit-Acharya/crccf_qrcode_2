from django.urls import path

from . import views


urlpatterns = [
    path("employees/add/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_update, name="employee_update"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),
    path("employees/<int:pk>/qr/", views.employee_qr_download, name="employee_qr_download"),
    path("employee/<str:employee_id>/", views.employee_public, name="employee_public"),
    path("api/employee/<str:employee_id>/", views.employee_api, name="employee_api"),
]
