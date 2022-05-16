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


class Requisite(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование реквизита (например, ИНН)')
    value = models.CharField(max_length=255, verbose_name='Значение реквизита')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "реквизит"
        verbose_name_plural = "Реквизиты"


class Position(models.Model):
    title = models.CharField(max_length=255, verbose_name='Наименование')
    unit = models.CharField(max_length=100, verbose_name='Единица измерения')
    price = models.CharField(max_length=100, verbose_name='Цена')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "позицию прайс-листа"
        verbose_name_plural = "Прайс-лист"
