from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import date
from decimal import Decimal, InvalidOperation
from django.db import models
import re
import html
from core.models import Note, Project, UserPresence, Customer, CustomerQuote


def _extract_task_lines_from_content(content):
    if not content:
        return []

    normalized = (
        content
        .replace('</div>', '\n')
        .replace('</p>', '\n')
        .replace('<br>', '\n')
        .replace('<br/>', '\n')
        .replace('<br />', '\n')
    )
    plain_text = html.unescape(strip_tags(normalized))

    tasks = []
    task_pattern = re.compile(r'^\+\s*(?:\[@([^\]]+)\]\s*)?(.*)$')

    for line in plain_text.splitlines():
        current_line = line.strip()
        if not current_line:
            continue

        match = task_pattern.match(current_line)
        if not match:
            continue

        username = (match.group(1) or '').strip()
        task_text = (match.group(2) or '').strip()
        if not task_text:
            continue

        tasks.append({
            'username': username,
            'text': task_text,
        })

    return tasks


def _sync_note_tasks(note):
    if note.category == 'task':
        return

    extracted_tasks = _extract_task_lines_from_content(note.content or '')
    existing_tasks = list(note.child_tasks.filter(category='task').select_related('assigned_user'))
    existing_by_key = {
        ((task.title or '').strip().lower(), task.assigned_user_id): task
        for task in existing_tasks
    }

    if not extracted_tasks:
        note.child_tasks.filter(category='task').delete()
        return

    seen_task_ids = set()

    for item in extracted_tasks:
        assigned_user = note.user
        if item['username']:
            mentioned_user = User.objects.filter(username__iexact=item['username']).first()
            if mentioned_user:
                assigned_user = mentioned_user

        task_title = item['text'][:255]
        lookup_key = (task_title.strip().lower(), assigned_user.id if assigned_user else None)
        existing_task = existing_by_key.get(lookup_key)

        if existing_task:
            existing_task.content = item['text']
            existing_task.assigned_project = note.assigned_project
            existing_task.parent_note = note
            existing_task.save(update_fields=['content', 'assigned_project', 'parent_note', 'updated_at'])
            seen_task_ids.add(existing_task.id)
            continue

        Note.objects.create(
            user=note.user,
            title=task_title,
            content=item['text'],
            category='task',
            assigned_user=assigned_user,
            assigned_project=note.assigned_project,
            parent_note=note,
        )

    stale_tasks = [task.id for task in existing_tasks if task.id not in seen_task_ids]
    if stale_tasks:
        Note.objects.filter(id__in=stale_tasks).delete()

@login_required
def note_index(request, pk=None):
    notes = Note.objects.filter(user=request.user).exclude(category='task').select_related('assigned_user', 'assigned_project')
    
    # Filtering based on GET parameters
    category_filter = request.GET.get('category')
    if category_filter:
        notes = notes.filter(category=category_filter)
        
    favorite_filter = request.GET.get('favorite')
    if favorite_filter == '1':
        notes = notes.filter(is_favorite=True)
        
    tag_filter = request.GET.get('tag')
    if tag_filter:
        notes = notes.filter(tags__name=tag_filter)
    
    active_note = None
    
    if pk:
        active_note = get_object_or_404(Note, pk=pk, user=request.user)
    elif notes.exists():
        active_note = notes.first()

    projects = Project.objects.filter(user=request.user).select_related('representative').prefetch_related('participants')
    users = User.objects.order_by('username')
        
    context = {
        'notes': notes,
        'active_note': active_note,
        'projects': projects,
        'users': users,
    }
    return render(request, 'core/index.html', context)

@login_required
def note_create(request):
    if request.method == 'POST':
        note = Note.objects.create(
            user=request.user,
            title='Yeni Not',
            content=''
        )
        messages.success(request, 'Yeni not oluşturuldu.')
        return redirect('note_detail', pk=note.pk)
    
    return redirect('index')

@login_required
def note_save(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', 'İsimsiz Not').strip()
        content = request.POST.get('content', '')
        category = request.POST.get('category', 'note')
        is_favorite = request.POST.get('is_favorite') == 'true'
        tags_raw = request.POST.get('tags', '')
        
        if not title:
            title = 'İsimsiz Not'
            
        note.title = title
        note.content = content
        note.category = category
        note.is_favorite = is_favorite
        note.save()

        _sync_note_tasks(note)
        
        # Handle Tags (comma separated names)
        note.tags.clear()
        if tags_raw:
            tag_names = [t.strip() for t in tags_raw.split(',') if t.strip()]
            from core.models import Tag # import here locally if we need to avoid circular, but we already have Note, maybe we need Tag
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name, user=request.user)
                note.tags.add(tag)
        
        messages.success(request, 'Not kaydedildi.')
        
    return redirect('note_detail', pk=note.pk)

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    
    # Check both GET and POST for maximum compatibility with the UI
    note.delete()
    messages.success(request, 'Not silindi.')
        
    return redirect('index')

@login_required
def note_toggle_favorite(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

    note = get_object_or_404(Note, pk=pk, user=request.user)
    is_favorite = request.POST.get('is_favorite') == 'true'
    note.is_favorite = is_favorite
    note.save(update_fields=['is_favorite', 'updated_at'])

    return JsonResponse({'success': True, 'is_favorite': note.is_favorite})


@login_required
def project_create(request):
    if request.method != 'POST':
        return redirect('projects')

    name = request.POST.get('name', '').strip()
    color = request.POST.get('color', 'blue-500').strip() or 'blue-500'
    representative_id = request.POST.get('representative_id')
    participant_ids = request.POST.getlist('participant_ids')
    description = request.POST.get('description', '').strip()

    if not name:
        messages.error(request, 'Proje adı zorunludur.')
        next_url = request.POST.get('next') or 'projects'
        return redirect(next_url)

    representative = None
    if representative_id:
        representative = User.objects.filter(id=representative_id).first()

    project = Project.objects.create(
        user=request.user,
        name=name,
        color=color,
        representative=representative,
        description=description,
    )

    if participant_ids:
        participants = User.objects.filter(id__in=participant_ids)
        project.participants.set(participants)

    messages.success(request, 'Proje oluşturuldu.')
    next_url = request.POST.get('next') or 'projects'
    return redirect(next_url)


@login_required
def note_assign(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed.'}, status=405)

    note = get_object_or_404(Note, pk=pk, user=request.user)
    assign_type = request.POST.get('assign_type')
    target_id = request.POST.get('target_id')

    if assign_type == 'clear':
        note.assigned_user = None
        note.assigned_project = None
        note.save(update_fields=['assigned_user', 'assigned_project', 'updated_at'])
        return JsonResponse({'success': True, 'assigned_user': None, 'assigned_project': None})

    if assign_type == 'user':
        user = User.objects.filter(id=target_id).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'Kullanıcı bulunamadı.'}, status=404)
        note.assigned_user = user
        note.assigned_project = None
        note.save(update_fields=['assigned_user', 'assigned_project', 'updated_at'])
        return JsonResponse({'success': True, 'assigned_user': user.username, 'assigned_project': None})

    if assign_type == 'project':
        project = Project.objects.filter(id=target_id, user=request.user).first()
        if not project:
            return JsonResponse({'success': False, 'message': 'Proje bulunamadı.'}, status=404)
        note.assigned_project = project
        note.assigned_user = None
        note.save(update_fields=['assigned_user', 'assigned_project', 'updated_at'])
        return JsonResponse({'success': True, 'assigned_user': None, 'assigned_project': project.name})

    return JsonResponse({'success': False, 'message': 'Geçersiz atama tipi.'}, status=400)


@login_required
def project_index(request):
    projects = Project.objects.filter(user=request.user).select_related('representative').prefetch_related('participants', 'notes')
    users = User.objects.order_by('username')

    context = {
        'projects': projects,
        'users': users,
    }
    return render(request, 'core/projects.html', context)


@login_required
def task_index(request):
    tasks = Note.objects.filter(user=request.user, category='task').select_related('assigned_user', 'assigned_project', 'parent_note')
    active_tasks = tasks.filter(is_completed=False)
    archived_tasks = tasks.filter(is_completed=True)
    my_tasks = active_tasks.filter(assigned_user=request.user)
    project_tasks_count = active_tasks.exclude(assigned_project__isnull=True).count()

    context = {
        'tasks': tasks,
        'active_tasks': active_tasks,
        'archived_tasks': archived_tasks,
        'my_tasks': my_tasks,
        'project_tasks_count': project_tasks_count,
    }
    return render(request, 'core/tasks.html', context)


@login_required
def task_toggle_complete(request, pk):
    if request.method != 'POST':
        return redirect('tasks')

    task = get_object_or_404(Note, pk=pk, user=request.user, category='task')
    mark_completed = request.POST.get('complete') == '1'

    task.is_completed = mark_completed
    task.completed_at = timezone.now() if mark_completed else None
    task.save(update_fields=['is_completed', 'completed_at', 'updated_at'])

    next_url = request.POST.get('next') or 'tasks'
    return redirect(next_url)


@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('representative').prefetch_related('participants', 'notes__user', 'notes__assigned_user'),
        pk=pk,
        user=request.user
    )

    project_tasks = project.notes.filter(category='task').select_related('user', 'assigned_user')
    project_notes = project.notes.exclude(category='task').select_related('user', 'assigned_user')

    participant_users = list(project.participants.all())
    if project.representative and project.representative not in participant_users:
        participant_users.append(project.representative)

    context = {
        'project': project,
        'project_tasks': project_tasks,
        'project_notes': project_notes,
        'project_users': participant_users,
    }
    return render(request, 'core/project_detail.html', context)


@login_required
def customer_index(request):
    customers = Customer.objects.filter(user=request.user).prefetch_related('quotes')
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    if query:
        customers = customers.filter(
            models.Q(name__icontains=query)
            | models.Q(company_name__icontains=query)
            | models.Q(sector__icontains=query)
            | models.Q(email__icontains=query)
            | models.Q(phone__icontains=query)
        )

    if status:
        customers = customers.filter(status=status)

    context = {
        'customers': customers,
        'query': query,
        'status_filter': status,
        'customer_statuses': Customer.STATUS_CHOICES,
    }
    return render(request, 'core/customers.html', context)


@login_required
def customer_create(request):
    if request.method != 'POST':
        return redirect('customers')

    name = request.POST.get('name', '').strip()
    if not name:
        messages.error(request, 'Müşteri adı zorunludur.')
        return redirect('customers')

    allowed_customer_statuses = {choice[0] for choice in Customer.STATUS_CHOICES}
    selected_status = request.POST.get('status', 'lead') or 'lead'
    if selected_status not in allowed_customer_statuses:
        selected_status = 'lead'

    customer = Customer.objects.create(
        user=request.user,
        name=name,
        company_name=request.POST.get('company_name', '').strip(),
        sector=request.POST.get('sector', '').strip(),
        title=request.POST.get('title', '').strip(),
        email=request.POST.get('email', '').strip(),
        phone=request.POST.get('phone', '').strip(),
        alternate_phone=request.POST.get('alternate_phone', '').strip(),
        website=request.POST.get('website', '').strip(),
        city=request.POST.get('city', '').strip(),
        country=request.POST.get('country', '').strip(),
        address=request.POST.get('address', '').strip(),
        tax_office=request.POST.get('tax_office', '').strip(),
        tax_number=request.POST.get('tax_number', '').strip(),
        preferred_contact_channel=request.POST.get('preferred_contact_channel', '').strip(),
        status=selected_status,
        source=request.POST.get('source', '').strip(),
        budget_expectation=request.POST.get('budget_expectation', '').strip(),
        notes=request.POST.get('notes', '').strip(),
    )

    messages.success(request, 'Müşteri oluşturuldu.')
    return redirect('customer_detail', pk=customer.pk)


def _safe_parse_date(date_text):
    if not date_text:
        return None
    try:
        return date.fromisoformat(date_text)
    except ValueError:
        return None


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_customer':
            allowed_customer_statuses = {choice[0] for choice in Customer.STATUS_CHOICES}
            selected_status = request.POST.get('status', 'lead') or 'lead'
            if selected_status not in allowed_customer_statuses:
                selected_status = 'lead'

            customer.name = request.POST.get('name', customer.name).strip() or customer.name
            customer.company_name = request.POST.get('company_name', '').strip()
            customer.sector = request.POST.get('sector', '').strip()
            customer.title = request.POST.get('title', '').strip()
            customer.email = request.POST.get('email', '').strip()
            customer.phone = request.POST.get('phone', '').strip()
            customer.alternate_phone = request.POST.get('alternate_phone', '').strip()
            customer.website = request.POST.get('website', '').strip()
            customer.city = request.POST.get('city', '').strip()
            customer.country = request.POST.get('country', '').strip()
            customer.address = request.POST.get('address', '').strip()
            customer.tax_office = request.POST.get('tax_office', '').strip()
            customer.tax_number = request.POST.get('tax_number', '').strip()
            customer.preferred_contact_channel = request.POST.get('preferred_contact_channel', '').strip()
            customer.status = selected_status
            customer.source = request.POST.get('source', '').strip()
            customer.budget_expectation = request.POST.get('budget_expectation', '').strip()
            customer.notes = request.POST.get('notes', '').strip()
            customer.save()
            messages.success(request, 'Müşteri bilgileri güncellendi.')
            return redirect('customer_detail', pk=customer.pk)

        if action == 'create_quote':
            quote_title = request.POST.get('quote_title', '').strip()
            quote_amount_raw = request.POST.get('quote_amount', '0').strip() or '0'
            quote_date_value = _safe_parse_date(request.POST.get('quote_date', '').strip())

            if not quote_title:
                messages.error(request, 'Teklif başlığı zorunludur.')
                return redirect('customer_detail', pk=customer.pk)

            if not quote_date_value:
                messages.error(request, 'Teklif tarihi geçersiz.')
                return redirect('customer_detail', pk=customer.pk)

            try:
                quote_amount = Decimal(quote_amount_raw)
            except InvalidOperation:
                messages.error(request, 'Teklif tutarı sayısal olmalı.')
                return redirect('customer_detail', pk=customer.pk)

            allowed_quote_statuses = {choice[0] for choice in CustomerQuote.STATUS_CHOICES}
            selected_quote_status = request.POST.get('quote_status', 'draft') or 'draft'
            if selected_quote_status not in allowed_quote_statuses:
                selected_quote_status = 'draft'

            allowed_currencies = {choice[0] for choice in CustomerQuote.CURRENCY_CHOICES}
            selected_currency = request.POST.get('currency', 'TRY') or 'TRY'
            if selected_currency not in allowed_currencies:
                selected_currency = 'TRY'

            CustomerQuote.objects.create(
                user=request.user,
                customer=customer,
                title=quote_title,
                description=request.POST.get('quote_description', '').strip(),
                reference_code=request.POST.get('reference_code', '').strip(),
                amount=quote_amount,
                currency=selected_currency,
                quote_date=quote_date_value,
                valid_until=_safe_parse_date(request.POST.get('valid_until', '').strip()),
                follow_up_date=_safe_parse_date(request.POST.get('follow_up_date', '').strip()),
                status=selected_quote_status,
                notes=request.POST.get('quote_notes', '').strip(),
            )
            messages.success(request, 'Müşteri teklifi eklendi.')
            return redirect('customer_detail', pk=customer.pk)

    quotes = customer.quotes.all()
    context = {
        'customer': customer,
        'quotes': quotes,
        'customer_statuses': Customer.STATUS_CHOICES,
        'quote_statuses': CustomerQuote.STATUS_CHOICES,
        'currency_choices': CustomerQuote.CURRENCY_CHOICES,
    }
    return render(request, 'core/customer_detail.html', context)


@login_required
def user_summary(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    presence = UserPresence.objects.filter(user=user_obj).first()

    position = 'User'
    if user_obj.is_superuser:
        position = 'Administrator'
    elif user_obj.is_staff:
        position = 'Moderator'

    assigned_tasks_count = Note.objects.filter(assigned_user=user_obj, category='task').count()
    assigned_notes_count = Note.objects.filter(assigned_user=user_obj).exclude(category='task').count()
    assigned_projects_count = Project.objects.filter(participants=user_obj).count() + Project.objects.filter(representative=user_obj).exclude(participants=user_obj).count()

    recent_actions = []

    own_recent_notes = Note.objects.filter(user=user_obj).order_by('-updated_at')[:5]
    for note in own_recent_notes:
        recent_actions.append({
            'date': note.updated_at,
            'text': f"'{note.title}' notunu güncelledi.",
        })

    recent_assigned_notes = Note.objects.filter(assigned_user=user_obj).order_by('-updated_at')[:5]
    for note in recent_assigned_notes:
        action_label = 'göreve' if note.category == 'task' else 'nota'
        recent_actions.append({
            'date': note.updated_at,
            'text': f"'{note.title}' {action_label} atandı.",
        })

    recent_represented_projects = Project.objects.filter(representative=user_obj).order_by('-updated_at')[:5]
    for project in recent_represented_projects:
        recent_actions.append({
            'date': project.updated_at,
            'text': f"'{project.name}' projesinde temsilci.",
        })

    recent_actions = sorted(recent_actions, key=lambda item: item['date'], reverse=True)[:6]

    return JsonResponse({
        'success': True,
        'id': user_obj.id,
        'username': user_obj.username,
        'position': position,
        'registered_at': user_obj.date_joined.strftime('%d.%m.%Y %H:%M') if user_obj.date_joined else '-',
        'last_active': (
            presence.last_active_at.strftime('%d.%m.%Y %H:%M')
            if presence else (user_obj.last_login.strftime('%d.%m.%Y %H:%M') if user_obj.last_login else '-')
        ),
        'assigned_tasks': assigned_tasks_count,
        'assigned_notes': assigned_notes_count,
        'assigned_projects': assigned_projects_count,
        'recent_actions': [
            {
                'date': action['date'].strftime('%d.%m.%Y %H:%M'),
                'text': action['text'],
            }
            for action in recent_actions
        ],
    })
