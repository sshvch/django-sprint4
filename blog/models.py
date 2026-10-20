from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    title = models.CharField(
        "Заголовок",
        max_length=256,
        blank=False,
    )
    description = models.TextField(
        "Описание",
        blank=False,
    )
    slug = models.SlugField(
        "Идентификатор",
        unique=True,
        blank=False,
        help_text=(
            "Идентификатор страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        ),
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        blank=False,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True,
        blank=False,
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"


class Location(models.Model):
    name = models.CharField(
        "Название места",
        max_length=256,
        blank=False,
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        blank=False,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True,
        blank=False,
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"


class Post(models.Model):
    image = models.ImageField(
        "Изображение",
        upload_to="post_images/",
        blank=True,
    )
    title = models.CharField(
        "Заголовок",
        max_length=256,
        blank=False,
    )
    text = models.TextField(
        "Текст",
        blank=False,
    )
    pub_date = models.DateTimeField(
        "Дата и время публикации",
        blank=False,
        help_text=(
            "Если установить дату и время в будущем — можно делать "
            "отложенные публикации."
        ),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        blank=False,
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        verbose_name="Местоположение",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        verbose_name="Категория",
        null=True,
        blank=False,
    )
    is_published = models.BooleanField(
        "Опубликовано",
        default=True,
        blank=False,
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True,
        blank=False,
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Добавлено")

    class Meta:
        ordering = ("created_at",)
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:20]
