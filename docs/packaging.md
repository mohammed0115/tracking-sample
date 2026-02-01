# Packaging & Deployment Notes

## Local Packaging Checklist
- [ ] `python manage.py check`
- [ ] `python manage.py test`
- [ ] `python manage.py create_groups`
- [ ] `python manage.py seed_samples`

## Deployment Notes (Windows)
- Use a production WSGI server (e.g., gunicorn on Linux, or IIS/Waitress on Windows).
- Configure environment variables for `SECRET_KEY` and database settings.
- Set `DEBUG = False` and configure `ALLOWED_HOSTS`.

## Suggested Production Steps
```powershell
python manage.py check
python manage.py test
```

> Adjust database and static files configuration for your hosting environment.
