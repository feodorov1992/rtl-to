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


class Vacancy(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название вакансии')
    salary = models.FloatField(verbose_name='Заработная плата', null=True, blank=True)
    created_at = models.DateField(auto_now_add=True)
    body = RichTextField(verbose_name='Описание вакансии')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'вакансия'
        verbose_name_plural = 'вакансии'
