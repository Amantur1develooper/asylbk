from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db.models import Q

from .models import Category, KnowledgePost, KnowledgeFile
from .forms import KnowledgePostForm


def _can_edit(user, post):
    """Редактировать может автор или руководство."""
    if user.is_superuser:
        return True
    if post.author == user:
        return True
    return user.role in ('director', 'deputy_director', 'manager', 'managing_partner_advocate', 'admin')


class PostListView(LoginRequiredMixin, ListView):
    template_name      = 'knowledge/list.html'
    model              = KnowledgePost
    context_object_name = 'posts'
    paginate_by        = 20

    def get_queryset(self):
        qs = KnowledgePost.objects.select_related('author', 'category').prefetch_related('files')
        q  = self.request.GET.get('q', '').strip()
        cat = self.request.GET.get('cat', '')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))
        if cat:
            qs = qs.filter(category__id=cat)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.all()
        ctx['q']          = self.request.GET.get('q', '')
        ctx['cat']        = self.request.GET.get('cat', '')
        return ctx


class PostDetailView(LoginRequiredMixin, DetailView):
    template_name       = 'knowledge/detail.html'
    model               = KnowledgePost
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['can_edit'] = _can_edit(self.request.user, self.object)
        return ctx


@login_required
def post_create(request):
    form = KnowledgePostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        for f in request.FILES.getlist('upload_files'):
            KnowledgeFile.objects.create(post=post, file=f)
        messages.success(request, 'Запись добавлена.')
        return redirect('knowledge:detail', pk=post.pk)
    return render(request, 'knowledge/form.html', {'form': form, 'action': 'Создать'})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(KnowledgePost, pk=pk)
    if not _can_edit(request.user, post):
        messages.error(request, 'Нет доступа.')
        return redirect('knowledge:detail', pk=pk)
    form = KnowledgePostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        form.save()
        for f in request.FILES.getlist('upload_files'):
            KnowledgeFile.objects.create(post=post, file=f)
        # Удаление выбранных файлов
        delete_ids = request.POST.getlist('delete_files')
        if delete_ids:
            KnowledgeFile.objects.filter(pk__in=delete_ids, post=post).delete()
        messages.success(request, 'Запись обновлена.')
        return redirect('knowledge:detail', pk=post.pk)
    return render(request, 'knowledge/form.html', {
        'form': form, 'post': post, 'action': 'Сохранить',
        'files': post.files.all(),
    })


@login_required
def post_delete(request, pk):
    post = get_object_or_404(KnowledgePost, pk=pk)
    if not _can_edit(request.user, post):
        messages.error(request, 'Нет доступа.')
        return redirect('knowledge:detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Запись удалена.')
        return redirect('knowledge:list')
    return render(request, 'knowledge/confirm_delete.html', {'post': post})
