# RFID Sample Tracking (Django)

A Django web application for managing forensic/lab samples with RFID verification, role-based access control, and audit logging.

## Features
- Role-based access control: Admin, Operator, Viewer
- Sample list, add, and detail workflows
- RFID check and approval workflow
- Audit log tracking for key actions (login, RFID check, approve, reject)
- Arabic UI with RTL layout and i18n-ready templates

## Tech Stack
- Django 5.x
- Django REST Framework
- SQLite (default, can be replaced)

## Roles & Permissions
- **Admin**: Full permissions on `Sample`, `RFIDTag`, `AuditLog`
- **Operator**: `view` + `change` on `Sample` & `RFIDTag`, `view` on `AuditLog`
- **Viewer**: `view` on all models

Groups are created via the `create_groups` management command.

## Key URLs
- Web list: `/api/samples/web/`
- Add sample: `/api/samples/add/`
- Sample detail: `/api/samples/full/<sample_number>/`
- Login: `/users/login/`
- Logout: `/users/logout/`

## Management Commands
- Create roles and permissions:
  ```powershell
  python manage.py create_groups
  ```
- Seed sample data:
  ```powershell
  python manage.py seed_samples
  ```

## Running Tests
```powershell
python manage.py test
```

## Security Notes
- All web views require authentication.
- CSRF protection is enabled for all POST forms.
- RFID check and approval are restricted to Admin/Operator via permissions.

## SRS Traceability
See the traceability matrix in [docs/srs-traceability.md](docs/srs-traceability.md).

## Manual Verification & Packaging
- [docs/manual-verification.md](docs/manual-verification.md)
- [docs/packaging.md](docs/packaging.md)
"# tracking-sample" 
