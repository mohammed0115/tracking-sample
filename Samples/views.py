# Role-based access control helpers
from django.contrib.auth.decorators import user_passes_test, permission_required
from django.http import HttpResponseForbidden, HttpResponse

def is_admin(user):
	return user.groups.filter(name='Admin').exists()

def is_operator(user):
	return user.groups.filter(name='Operator').exists()

def is_operator_or_admin(user):
	return user.groups.filter(name__in=['Admin', 'Operator']).exists()
# View for full screen sample details and actions
from django.contrib.auth.decorators import login_required
from .models import AuditLog
from django.shortcuts import get_object_or_404

@login_required
@permission_required('Samples.view_sample', raise_exception=True)
def sample_full_screen_view(request, sample_number):
	sample = get_object_or_404(Sample, sample_number=sample_number)
	can_act = is_operator_or_admin(request.user)
	if request.method == 'POST':
		if not request.user.has_perm('Samples.change_sample'):
			return HttpResponseForbidden()
		if not can_act:
			return HttpResponseForbidden()
		action = request.POST.get('action')
		if action == 'rfid_check' and sample.status == 'pending':
			sample.status = 'checked'
			sample.save()
			AuditLog.objects.create(
				user=request.user,
				sample=sample,
				action=f"فحص RFID (UID: {sample.rfid.uid})"
			)
		elif action == 'approve' and sample.status == 'checked':
			sample.status = 'approved'
			sample.save()
			AuditLog.objects.create(user=request.user, sample=sample, action='اعتماد العينة')
		elif action == 'reject' and sample.status in ['pending', 'checked', 'approved']:
			sample.status = 'rejected'
			sample.save()
			AuditLog.objects.create(user=request.user, sample=sample, action='رفض العينة')
		return redirect('sample_full_screen', sample_number=sample.sample_number)
	logs = AuditLog.objects.filter(sample=sample).order_by('-timestamp')[:10]
	return render(
		request,
		'Samples/sample_full_screen.html',
		{'sample': sample, 'can_act': can_act, 'logs': logs}
	)
## Removed unused ListView import
from django.shortcuts import render, redirect
# ...existing code...


# Web view for listing samples
@login_required
@permission_required('Samples.view_sample', raise_exception=True)
def sample_list_view(request):
	query, sample_type, category, date_value, samples = _get_filtered_samples(request)

	from django.core.paginator import Paginator
	paginator = Paginator(samples, 10)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	context = {
		'samples': page_obj.object_list,
		'page_obj': page_obj,
		'query': query,
		'sample_type': sample_type,
		'category': category,
		'date_value': date_value,
	}
	return render(request, 'Samples/sample_list.html', context)


def _get_filtered_samples(request):
	query = request.GET.get('q', '').strip()
	sample_type = request.GET.get('sample_type', '').strip()
	category = request.GET.get('category', '').strip()
	date_value = request.GET.get('date', '').strip()

	samples = Sample.objects.all().order_by('-collected_date', '-id')
	if sample_type:
		samples = samples.filter(sample_type=sample_type)
	if category:
		samples = samples.filter(category=category)
	if date_value:
		samples = samples.filter(collected_date=date_value)
	if query:
		from django.db.models import Q
		samples = samples.filter(
			Q(sample_number__icontains=query) | Q(person_name__icontains=query)
		)

	return query, sample_type, category, date_value, samples


@login_required
@permission_required('Samples.view_sample', raise_exception=True)
def export_samples_view(request):
	query, sample_type, category, date_value, samples = _get_filtered_samples(request)

	from io import BytesIO
	from openpyxl import Workbook

	wb = Workbook()
	ws = wb.active
	ws.title = 'Samples'

	ws.append(['Sample Number', 'Person Name', 'Type', 'Category', 'Date', 'Status', 'RFID'])
	for s in samples:
		ws.append([
			s.sample_number,
			s.person_name,
			s.sample_type,
			s.category,
			s.collected_date.strftime('%Y-%m-%d') if s.collected_date else '',
			s.status,
			s.rfid.uid,
		])

	output = BytesIO()
	wb.save(output)
	output.seek(0)

	response = HttpResponse(
		output.getvalue(),
		content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	)
	response['Content-Disposition'] = 'attachment; filename="samples_export.xlsx"'
	return response


def _can_export(user):
	return user.groups.filter(name__in=['Admin', 'Operator']).exists()


@login_required
@permission_required('Samples.view_auditlog', raise_exception=True)
def reports_view(request):
	report_type = request.GET.get('report_type', 'samples')
	from_date = request.GET.get('from_date', '').strip()
	to_date = request.GET.get('to_date', '').strip()
	user_id = request.GET.get('user_id', '').strip()

	from django.contrib.auth.models import User
	users = User.objects.all().order_by('username')

	columns, rows, title = _build_report(report_type, from_date, to_date, user_id)
	context = {
		'report_type': report_type,
		'from_date': from_date,
		'to_date': to_date,
		'user_id': user_id,
		'users': users,
		'columns': columns,
		'rows': rows,
		'title': title,
		'can_export': _can_export(request.user),
	}
	return render(request, 'Samples/reports.html', context)


def _build_report(report_type, from_date, to_date, user_id):
	from django.db.models import Q
	from django.utils.dateparse import parse_date
	from django.contrib.auth.models import User

	start = parse_date(from_date) if from_date else None
	end = parse_date(to_date) if to_date else None
	user_filter = User.objects.filter(id=user_id).first() if user_id else None

	def date_filter(qs, field):
		if start:
			qs = qs.filter(**{f"{field}__date__gte": start}) if field.endswith('timestamp') else qs.filter(**{f"{field}__gte": start})
		if end:
			qs = qs.filter(**{f"{field}__date__lte": end}) if field.endswith('timestamp') else qs.filter(**{f"{field}__lte": end})
		return qs

	def _make_columns(labels):
		return [{'label': label, 'is_status': label in ['الحالة', 'الحالة النهائية']} for label in labels]

	def _make_rows(columns, row_dicts):
		rows = []
		for row in row_dicts:
			cells = []
			for col in columns:
				cells.append({'value': row.get(col['label'], ''), 'is_status': col['is_status']})
			rows.append(cells)
		return rows

	if report_type == 'rfid':
		logs = AuditLog.objects.filter(action__startswith='فحص RFID')
		logs = date_filter(logs, 'timestamp')
		if user_filter:
			logs = logs.filter(user=user_filter)
			
		columns = _make_columns(['رقم العينة', 'UID', 'وقت الفحص', 'المستخدم', 'النتيجة'])
		row_dicts = []
		for log in logs.order_by('-timestamp'):
			uid = ''
			if 'UID:' in log.action:
				uid = log.action.split('UID:')[-1].strip(' )')
			row_dicts.append({
				'رقم العينة': log.sample.sample_number if log.sample else '-',
				'UID': uid,
				'وقت الفحص': log.timestamp.strftime('%Y-%m-%d %H:%M'),
				'المستخدم': log.user.username,
				'النتيجة': 'نجاح',
			})
		return columns, _make_rows(columns, row_dicts), 'تقرير فحص RFID'

	if report_type == 'approval':
		logs = AuditLog.objects.filter(action='اعتماد العينة')
		logs = date_filter(logs, 'timestamp')
		if user_filter:
			logs = logs.filter(user=user_filter)
		columns = _make_columns(['رقم العينة', 'تاريخ الاعتماد', 'المستخدم', 'الحالة النهائية', 'ملاحظات'])
		row_dicts = []
		for log in logs.order_by('-timestamp'):
			row_dicts.append({
				'رقم العينة': log.sample.sample_number if log.sample else '-',
				'تاريخ الاعتماد': log.timestamp.strftime('%Y-%m-%d %H:%M'),
				'المستخدم': log.user.username,
				'الحالة النهائية': 'معتمدة',
				'ملاحظات': '',
			})
		return columns, _make_rows(columns, row_dicts), 'تقرير الاعتماد'

	if report_type == 'audit':
		logs = AuditLog.objects.all()
		logs = date_filter(logs, 'timestamp')
		if user_filter:
			logs = logs.filter(user=user_filter)
		columns = _make_columns(['المستخدم', 'الإجراء', 'رقم العينة', 'التاريخ والوقت'])
		row_dicts = []
		for log in logs.order_by('-timestamp'):
			row_dicts.append({
				'المستخدم': log.user.username,
				'الإجراء': log.action,
				'رقم العينة': log.sample.sample_number if log.sample else '-',
				'التاريخ والوقت': log.timestamp.strftime('%Y-%m-%d %H:%M'),
			})
		return columns, _make_rows(columns, row_dicts), 'تقرير النشاط'

	# Default: samples report
	from .models import Sample
	samples = Sample.objects.all().order_by('-collected_date', '-id')
	if start:
		samples = samples.filter(collected_date__gte=start)
	if end:
		samples = samples.filter(collected_date__lte=end)
	if user_filter:
		# approver is derived from audit log
		pass
	columns = _make_columns(['رقم العينة', 'نوع العينة', 'التصنيف', 'تاريخ الجمع', 'الحالة', 'تم فحص RFID', 'المعتمد'])
	row_dicts = []
	# map approvals by sample
	approval_logs = AuditLog.objects.filter(action='اعتماد العينة')
	if user_filter:
		approval_logs = approval_logs.filter(user=user_filter)
	approval_map = {}
	for log in approval_logs.order_by('-timestamp'):
		if log.sample_id not in approval_map:
			approval_map[log.sample_id] = log.user.username
	status_map = {
		'pending': 'قيد الفحص',
		'checked': 'تم التحقق',
		'approved': 'معتمدة',
		'rejected': 'مرفوضة',
	}
	for s in samples:
		rfid_checked = 'نعم' if s.status in ['checked', 'approved'] else 'لا'
		row_dicts.append({
			'رقم العينة': s.sample_number,
			'نوع العينة': s.sample_type,
			'التصنيف': s.category,
			'تاريخ الجمع': s.collected_date.strftime('%Y-%m-%d') if s.collected_date else '',
			'الحالة': status_map.get(s.status, s.status),
			'تم فحص RFID': rfid_checked,
			'المعتمد': approval_map.get(s.id, '-'),
		})
	return columns, _make_rows(columns, row_dicts), 'تقرير العينات'


@login_required
@permission_required('Samples.view_auditlog', raise_exception=True)
def export_reports_excel(request):
	if not _can_export(request.user):
		return HttpResponseForbidden()
	report_type = request.GET.get('report_type', 'samples')
	from_date = request.GET.get('from_date', '').strip()
	to_date = request.GET.get('to_date', '').strip()
	user_id = request.GET.get('user_id', '').strip()
	columns, rows, title = _build_report(report_type, from_date, to_date, user_id)

	from io import BytesIO
	from openpyxl import Workbook
	
	wb = Workbook()
	ws = wb.active
	ws.title = 'Report'
	col_labels = [c['label'] for c in columns]
	ws.append(col_labels)
	for row in rows:
		ws.append([cell['value'] for cell in row])
	
	output = BytesIO()
	wb.save(output)
	output.seek(0)
	response = HttpResponse(
		output.getvalue(),
		content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
	)
	response['Content-Disposition'] = f'attachment; filename="{title}.xlsx"'
	return response


@login_required
@permission_required('Samples.view_auditlog', raise_exception=True)
def export_reports_pdf(request):
	if not _can_export(request.user):
		return HttpResponseForbidden()
	report_type = request.GET.get('report_type', 'samples')
	from_date = request.GET.get('from_date', '').strip()
	to_date = request.GET.get('to_date', '').strip()
	user_id = request.GET.get('user_id', '').strip()
	columns, rows, title = _build_report(report_type, from_date, to_date, user_id)

	from io import BytesIO
	from reportlab.lib.pagesizes import A4
	from reportlab.lib import colors
	from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
	from reportlab.lib.enums import TA_RIGHT
	from reportlab.lib.styles import ParagraphStyle
	from pathlib import Path

	def shape_text(text):
		try:
			import arabic_reshaper
			from bidi.algorithm import get_display
			return get_display(arabic_reshaper.reshape(str(text)))
		except Exception:
			return str(text)

	font_name = 'Helvetica'
	font_path = Path('static') / 'fonts' / 'Cairo-Regular.ttf'
	if font_path.exists():
		pdfmetrics.registerFont(TTFont('Cairo', str(font_path)))
		font_name = 'Cairo'

	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=A4)
	styles = getSampleStyleSheet()
	style_rtl = ParagraphStyle('rtl', parent=styles['Normal'], fontName=font_name, alignment=TA_RIGHT)
	story = [Paragraph(shape_text(title), ParagraphStyle('title', parent=styles['Title'], fontName=font_name, alignment=TA_RIGHT)), Spacer(1, 12)]

	col_labels = [c['label'] for c in columns]
	data = [[shape_text(c) for c in col_labels]] + [[shape_text(cell['value']) for cell in row] for row in rows]
	table = Table(data, hAlign='LEFT')
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
		('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
		('FONTNAME', (0, 0), (-1, -1), font_name),
		('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
	]))
	story.append(table)
	doc.build(story)

	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
	response.write(buffer.getvalue())
	return response

# Web view for adding a new sample
from .forms import SampleForm
from django.contrib.auth.decorators import login_required

@login_required
@permission_required('Samples.add_sample', raise_exception=True)
def add_sample_view(request):
	if request.method == 'POST':
		form = SampleForm(request.POST)
		if form.is_valid():
			form.save()
			if 'add_another' in request.POST:
				return redirect('add_sample')
			return redirect('sample-list-web')
	else:
		form = SampleForm()
	recent_samples = Sample.objects.all().order_by('-collected_date', '-id')[:5]
	return render(request, 'Samples/add_sample.html', {'form': form, 'samples': recent_samples})

# Dashboard view (alias of add_sample_view)
@login_required
@permission_required('Samples.view_sample', raise_exception=True)
def dashboard_view(request):
	return add_sample_view(request)

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import status
from .models import Sample
from .serializers import SampleSerializer
from django.shortcuts import get_object_or_404

class SampleListCreateAPIView(APIView):
	permission_classes = [IsAuthenticated, DjangoModelPermissions]
	def get(self, request):
		samples = Sample.objects.all()
		serializer = SampleSerializer(samples, many=True)
		return Response(serializer.data)

	def post(self, request):
		serializer = SampleSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SampleRetrieveUpdateDestroyAPIView(APIView):
	permission_classes = [IsAuthenticated, DjangoModelPermissions]
	def get_object(self, pk):
		return get_object_or_404(Sample, pk=pk)

	def get(self, request, pk):
		sample = self.get_object(pk)
		serializer = SampleSerializer(sample)
		return Response(serializer.data)

	def put(self, request, pk):
		sample = self.get_object(pk)
		serializer = SampleSerializer(sample, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def delete(self, request, pk):
		sample = self.get_object(pk)
		sample.delete()
		return Response(status=status.HTTP_204_NO_CONTENT)
