# CR Cyber Crime Foundation Employee QR Verification

A professional Django web app for managing employee records and downloading stable employee QR codes.

## Features

- Admin-only login and dashboard.
- Add, edit, delete, search, and filter employees.
- Public read-only employee verification page at `/employee/<employee_id>/`.
- Downloaded QR codes contain only a permanent employee profile URL.
- JSON API at `/api/employee/<employee_id>/`.
- SQLite by default, with settings kept simple for a later MySQL switch.

## QR Behavior

The downloaded QR image contains a stable employee verification page URL based on `employee_id`, for example `https://mydomain.com/employee/EMP001/`. It does not contain employee name, phone, department, designation, or other personal details as QR text.

The latest details live in the deployed Django database. When someone scans the QR, `/employee/<employee_id>/` loads and reads the latest active employee record from the database. If an admin edits employee details later, the same old QR shows the updated details without regenerating the QR.

## File Structure

```text
crccf_qrcode_2/
├── core/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── employees/
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   └── employees/css/styles.css
├── templates/
│   └── employees/
│       ├── base.html
│       ├── dashboard.html
│       ├── employee_confirm_delete.html
│       ├── employee_form.html
│       ├── login.html
│       └── public_employee.html
├── manage.py
├── requirements.txt
└── README.md
```

## Setup Commands

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open:

- Admin dashboard: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Django admin: `http://127.0.0.1:8000/django-admin/`
- Public verification example: `http://127.0.0.1:8000/employee/EMP001/`

The account used for this app must be staff or superuser. Non-admin accounts are rejected at login.

## Deployment Notes

Set these environment variables on the deployed backend:

- `ALLOWED_HOSTS=mydomain.com,www.mydomain.com`
- `PUBLIC_SITE_URL=https://mydomain.com`

`PUBLIC_SITE_URL` is used when generating QR PNG files, so the QR points at your live domain after deployment.
