# Manual End-to-End Verification

> Follow these steps after running the server to validate the complete workflow.

## 1) Start server
```powershell
python manage.py runserver
```

## 2) Login flow
- Open: `/users/login/`
- Login as Admin or Operator
- Expected: redirect to sample list and an `AuditLog` entry for login.

## 3) Sample list
- Open: `/api/samples/web/`
- Validate table render, filters, pagination links, and view action.
- Try filter by sample type, category, date, and search.

## 4) Add sample (dashboard)
- Open: `/api/samples/add/`
- Submit a new sample with RFID tag.
- Expected: sample added and visible in the “latest samples” table.

## 5) Sample details + RFID
- Open: `/api/samples/full/<sample_number>/`
- Click “قراءة RFID”.
- Expected: status changes to “تم الفحص”, audit log entry created.

## 6) Approve
- Click “اعتماد”.
- Expected: status changes to “معتمدة”, audit log entry created.

## 7) Permission checks
- Login as Viewer.
- Try RFID/Approve actions: expected 403 Forbidden.

## 8) Logout
- Click “تسجيل خروج”.
- Expected: redirected to login page.
