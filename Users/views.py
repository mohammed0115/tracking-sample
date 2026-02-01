
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from .forms import UserRegisterForm, UserProfileForm, AdminUserCreateForm, AdminUserEditForm
from django.core.mail import send_mail
from django.conf import settings

def register_view(request):
	if request.method == 'POST':
		form = UserRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('login')
	else:
		form = UserRegisterForm()
	return render(request, 'Users/register.html', {'form': form})

from Samples.models import AuditLog

def is_admin(user):
	return user.groups.filter(name='Admin').exists()

def login_view(request):
	if request.method == 'POST':
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			# سجل الدخول في AuditLog
			AuditLog.objects.create(user=user, action="تسجيل الدخول")
			redirect_to = request.POST.get('next') or request.GET.get('next') or '/api/samples/web/'
			return redirect(redirect_to)
	else:
		form = AuthenticationForm()
	return render(request, 'Users/login.html', {'form': form})

def logout_view(request):
	logout(request)
	return redirect('login')

def password_reset_view(request):
	if request.method == 'POST':
		form = PasswordResetForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			users = User.objects.filter(email=email)
			for user in users:
				# Send reset email (simplified, for production use Django's built-in)
				pass
			return render(request, 'Users/password_reset_done.html')
	else:
		form = PasswordResetForm()
	return render(request, 'Users/password_reset.html', {'form': form})

def password_reset_confirm_view(request, uidb64, token):
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None
	if user is not None and default_token_generator.check_token(user, token):
		if request.method == 'POST':
			form = SetPasswordForm(user, request.POST)
			if form.is_valid():
				form.save()
				return redirect('login')
		else:
			form = SetPasswordForm(user)
		return render(request, 'Users/password_reset_confirm.html', {'form': form})
	else:
		return render(request, 'Users/password_reset_invalid.html')

@login_required
def profile_edit_view(request):
	if request.method == 'POST':
		form = UserProfileForm(request.POST, request.FILES, instance=request.user)
		if form.is_valid():
			user = form.save(commit=False)
			avatar = form.cleaned_data.get('avatar')
			user.save()
			if avatar:
				profile = user.userprofile
				profile.avatar = avatar
				profile.save()
			AuditLog.objects.create(user=request.user, action='User updated own profile')
			return redirect('profile_edit')
	else:
		form = UserProfileForm(instance=request.user)
	return render(request, 'Users/profile_edit.html', {'form': form})


@login_required
@user_passes_test(is_admin, login_url='/users/login/')
def user_management_view(request):
	users = User.objects.all().order_by('username')
	user_rows = []
	for u in users:
		role = u.groups.first().name if u.groups.exists() else '-'
		user_rows.append({'user': u, 'role': role})
	return render(request, 'Users/user_management.html', {'user_rows': user_rows})


def _set_user_role(user, role_name):
	user.groups.clear()
	group, _ = Group.objects.get_or_create(name=role_name)
	user.groups.add(group)


@login_required
@user_passes_test(is_admin, login_url='/users/login/')
def user_create_view(request):
	if request.method == 'POST':
		form = AdminUserCreateForm(request.POST)
		if form.is_valid():
			user = form.save(commit=False)
			user.is_active = form.cleaned_data.get('is_active', True)
			user.save()
			_set_user_role(user, form.cleaned_data['role'])
			AuditLog.objects.create(user=request.user, action=f"إنشاء مستخدم: {user.username} ({form.cleaned_data['role']})")
			return redirect('user_management')
	else:
		form = AdminUserCreateForm()
	return render(request, 'Users/user_form.html', {'form': form, 'title': 'إضافة مستخدم'})


@login_required
@user_passes_test(is_admin, login_url='/users/login/')
def user_edit_view(request, user_id):
	user = User.objects.get(pk=user_id)
	current_role = user.groups.first().name if user.groups.exists() else 'Viewer'
	if request.method == 'POST':
		form = AdminUserEditForm(request.POST, instance=user)
		if form.is_valid():
			before_email = user.email
			before_first = user.first_name
			before_last = user.last_name
			before_active = user.is_active
			before_role = current_role
			
			user = form.save(commit=False)
			user.is_active = form.cleaned_data.get('is_active', True)
			user.save()
			_set_user_role(user, form.cleaned_data['role'])

			actions = []
			if before_email != user.email or before_first != user.first_name or before_last != user.last_name:
				actions.append('تعديل بيانات المستخدم')
			if before_active != user.is_active:
				actions.append('تفعيل المستخدم' if user.is_active else 'إيقاف المستخدم')
			if before_role != form.cleaned_data['role']:
				actions.append(f"تغيير دور المستخدم إلى {form.cleaned_data['role']}")
			for act in actions:
				AuditLog.objects.create(user=request.user, action=f"{act}: {user.username}")
			return redirect('user_management')
	else:
		form = AdminUserEditForm(instance=user, initial={'role': current_role, 'is_active': user.is_active})
	return render(request, 'Users/user_form.html', {'form': form, 'title': 'تعديل مستخدم', 'edit': True})


@login_required
@user_passes_test(is_admin, login_url='/users/login/')
def user_toggle_active_view(request, user_id):
	user = User.objects.get(pk=user_id)
	user.is_active = not user.is_active
	user.save()
	AuditLog.objects.create(user=request.user, action=f"{'تفعيل' if user.is_active else 'إيقاف'} المستخدم: {user.username}")
	return redirect('user_management')


@login_required
@user_passes_test(is_admin, login_url='/users/login/')
def user_reset_password_view(request, user_id):
	import secrets
	user = User.objects.get(pk=user_id)
	new_password = secrets.token_urlsafe(6)
	user.set_password(new_password)
	user.save()
	AuditLog.objects.create(user=request.user, action=f"إعادة تعيين كلمة المرور للمستخدم: {user.username}")
	return render(request, 'Users/password_reset_admin_result.html', {'target_user': user, 'new_password': new_password})
