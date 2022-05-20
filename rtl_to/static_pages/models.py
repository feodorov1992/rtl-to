from django.db import models
from ckeditor.fields import RichTextField


class MainTextBlock(models.Model):

    title = models.CharField(max_length=150, verbose_name='Заголовок')
    body = RichTextField(verbose_name='Текст')
    img = models.ImageField(verbose_name='Изображение', blank=True, null=True, upload_to='images')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "блок главной страницы"
        verbose_name_plural = "Главная страница"
