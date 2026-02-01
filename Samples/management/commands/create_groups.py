from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create Admin, Operator, and Viewer groups and assign permissions for Samples app.'

    def handle(self, *args, **options):
        # Models for which permissions will be assigned
        app_label = 'Samples'
        model_names = ['sample', 'rfidtag', 'auditlog']

        # Create or get groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        operator_group, _ = Group.objects.get_or_create(name='Operator')
        viewer_group, _ = Group.objects.get_or_create(name='Viewer')

        # Helper to collect perms
        def perms_for(model, perm_codes=None):
            ctype = ContentType.objects.get(app_label=app_label, model=model)
            if perm_codes is None:
                # return all perms for this content type
                return Permission.objects.filter(content_type=ctype)
            else:
                return Permission.objects.filter(content_type=ctype, codename__in=perm_codes)

        # Assign Admin: all permissions on all models
        for model in model_names:
            for p in perms_for(model):
                admin_group.permissions.add(p)

        # Assign Operator: view + change for Sample and RFIDTag, view for AuditLog
        sample_perms = perms_for('sample', perm_codes=['view_sample', 'change_sample'])
        rfid_perms = perms_for('rfidtag', perm_codes=['view_rfidtag', 'change_rfidtag'])
        audit_perms = perms_for('auditlog', perm_codes=['view_auditlog'])
        for p in list(sample_perms) + list(rfid_perms) + list(audit_perms):
            operator_group.permissions.add(p)

        # Assign Viewer: only view permissions for all models
        for model in model_names:
            view_perms = perms_for(model, perm_codes=[f'view_{model}'])
            for p in view_perms:
                viewer_group.permissions.add(p)

        self.stdout.write(self.style.SUCCESS('Groups and permissions created/updated.'))
