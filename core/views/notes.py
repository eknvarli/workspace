from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Note

@login_required
def note_index(request, pk=None):
    notes = request.user.notes.all()
    
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
        
    context = {
        'notes': notes,
        'active_note': active_note
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
