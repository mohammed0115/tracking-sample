# SRS Traceability Matrix

This document maps SRS requirements to implemented code locations.

## Functional Requirements

| ID | Requirement | Implementation Notes | Files/Areas |
|----|-------------|----------------------|-------------|
| FR-1 | تسجيل الدخول | Uses Django auth; login records `AuditLog` entry | Users `login_view`, `AuditLog` creation in `Users` app |
| FR-2 | عرض قائمة العينات مع فلترة | List view implemented; filtering can be extended | Samples `sample_list_view`, template list |
| FR-3 | عرض تفاصيل العينة | Sample detail screen shows metadata and status | Samples `sample_full_screen_view`, template |
| FR-4 | فحص RFID | Restricted to Admin/Operator; status -> `checked`; audit logged | `sample_full_screen_view` POST `action=rfid_check` |
| FR-5 | اعتماد العينة بعد RFID | Restricted; only after `checked`; audit logged | `sample_full_screen_view` POST `action=approve` |
| FR-6 | التعديل بعد الاعتماد | Allowed via change permissions; logs on change | `change_sample` permission, future form update logging |
| FR-7 | سجلات التدقيق | Logs for login, RFID, approve, reject | `AuditLog` model, `Users` + `Samples` views |

## Non-Functional Requirements

| ID | Requirement | Implementation Notes | Files/Areas |
|----|-------------|----------------------|-------------|
| NFR-1 | الأمان | Auth required; CSRF on POST forms; role permissions | Samples views, Users views, templates |
| NFR-2 | الموثوقية | Prevent approve before RFID; audit events | `sample_full_screen_view` logic |
| NFR-3 | القابلية للتوسع | RFIDTag model supports multiple tags; APIs available | `RFIDTag`, DRF APIViews |
| NFR-4 | سهولة الاستخدام | RTL UI, clear buttons and statuses | Templates in Samples/Users |

## Notes
- Filtering in FR-2 can be expanded with query parameters and UI controls.
- FR-6: If post-approval edits need explicit logging per field, add it to the edit flow in `SampleForm` handling.
