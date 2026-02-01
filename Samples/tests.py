from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse
from datetime import date

from .models import Sample, RFIDTag, AuditLog


class SampleWorkflowTests(TestCase):
	def setUp(self):
		self.operator_group, _ = Group.objects.get_or_create(name='Operator')
		self.viewer_group, _ = Group.objects.get_or_create(name='Viewer')

		self.view_sample_perm = Permission.objects.get(codename='view_sample')
		self.change_sample_perm = Permission.objects.get(codename='change_sample')

		self.operator = User.objects.create_user(username='operator', password='pass1234')
		self.operator.groups.add(self.operator_group)
		self.operator.user_permissions.add(self.view_sample_perm, self.change_sample_perm)

		self.viewer = User.objects.create_user(username='viewer', password='pass1234')
		self.viewer.groups.add(self.viewer_group)
		self.viewer.user_permissions.add(self.view_sample_perm)

		self.rfid = RFIDTag.objects.create(uid='RFID-TEST-0001')
		self.sample = Sample.objects.create(
			sample_number='S-0001',
			sample_type='دم',
			category='جنائية',
			person_name='يوسف أحمد',
			collected_date=date(2026, 2, 1),
			location='الرياض',
			rfid=self.rfid,
			status='pending'
		)

	def test_login_records_auditlog(self):
		url = reverse('login')
		response = self.client.post(url, {'username': 'operator', 'password': 'pass1234'})
		self.assertEqual(response.status_code, 302)
		self.assertTrue(AuditLog.objects.filter(user=self.operator, action='تسجيل الدخول').exists())

	def test_rfid_check_flow(self):
		self.client.force_login(self.operator)
		url = reverse('sample_full_screen', args=[self.sample.sample_number])
		response = self.client.post(url, {'action': 'rfid_check'})
		self.assertEqual(response.status_code, 302)
		self.sample.refresh_from_db()
		self.assertEqual(self.sample.status, 'checked')
		self.assertTrue(
			AuditLog.objects.filter(sample=self.sample, action__startswith='فحص RFID').exists()
		)

	def test_approve_requires_checked(self):
		self.client.force_login(self.operator)
		url = reverse('sample_full_screen', args=[self.sample.sample_number])
		response = self.client.post(url, {'action': 'approve'})
		self.assertEqual(response.status_code, 302)
		self.sample.refresh_from_db()
		self.assertNotEqual(self.sample.status, 'approved')

	def test_approve_after_checked(self):
		self.sample.status = 'checked'
		self.sample.save()
		self.client.force_login(self.operator)
		url = reverse('sample_full_screen', args=[self.sample.sample_number])
		response = self.client.post(url, {'action': 'approve'})
		self.assertEqual(response.status_code, 302)
		self.sample.refresh_from_db()
		self.assertEqual(self.sample.status, 'approved')
		self.assertTrue(
			AuditLog.objects.filter(sample=self.sample, action='اعتماد العينة').exists()
		)

	def test_viewer_cannot_post_actions(self):
		self.client.force_login(self.viewer)
		url = reverse('sample_full_screen', args=[self.sample.sample_number])
		response = self.client.post(url, {'action': 'rfid_check'})
		self.assertEqual(response.status_code, 403)
