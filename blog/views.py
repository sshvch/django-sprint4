from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


def index(request):
    template = "blog/index.html"
    post_list = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).order_by("-pub_date")

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}
    return render(request, template, context)


def post_detail(request, id):
    post = get_object_or_404(Post, pk=id)

    if request.user != post.author:
        if (
            not post.is_published
            or post.pub_date > timezone.now()
            or not post.category.is_published
        ):
            raise Http404("Пост не найден")

    comments = post.comments.all()
    form = CommentForm()

    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }
    return render(request, "blog/detail.html", context)


def category_posts(request, category_slug):
    _category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = Post.objects.filter(
        category=_category,
        pub_date__lte=timezone.now(),
        is_published=True,
    ).order_by("-pub_date")

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    authors = {post.author for post in post_list}
    context = {
        "category": _category,
        "page_obj": page_obj,
        "authors": authors,
    }
    return render(request, "blog/category.html", context)


from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileView(ListView):
    model = Post
    template_name = "blog/profile.html"
    context_object_name = "post_list"
    paginate_by = 10

    def get_queryset(self):
        # Получаем пользователя по username из URL
        self.profile_user = get_object_or_404(User, username=self.kwargs["username"])

        # Возвращаем посты этого пользователя
        return Post.objects.filter(author=self.profile_user).order_by("-pub_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Передаём в шаблон самого пользователя, чей профиль мы смотрим
        context["profile_user"] = self.profile_user
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"

    def test_func(self):
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("blog:post_detail", id=self.kwargs["post_id"])
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"id": self.object.id})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect("blog:post_detail", id=post_id)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/detail.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"id": self.kwargs["post_id"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(Post, id=self.kwargs["post_id"])
        context["comments"] = context["post"].comments.all()
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("blog:index")

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.object
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blog/detail.html"
    pk_url_kwarg = "comment_id"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"id": self.kwargs["post_id"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = get_object_or_404(Post, id=self.kwargs["post_id"])
        context["comments"] = context["post"].comments.all()
        return context
