from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Ad(models.Model):
    id = models.AutoField(verbose_name='ID', primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(verbose_name='Заголовок', max_length=100)
    description = models.TextField(verbose_name='Описание товара')
    image_url = models.CharField(verbose_name='Ссылка на изображение', max_length=200, blank=True, null=True)
    category = models.CharField(verbose_name='Категория товара', max_length=255)
    condition = models.CharField(verbose_name='Состояние товара', max_length=255)
    created_at = models.DateTimeField(verbose_name='Дата публикации объявления', auto_now_add=True)

    def __str__(self):
        return self.title


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('awaits', 'ожидает'),
        ('accepted', 'принята'),
        ('rejected', 'отклонена'),
    ]
    id = models.AutoField(verbose_name='ID', primary_key=True)
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление-отправитель',
                                  related_name='sent_proposals')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, verbose_name='Объявление-получатель',
                                    related_name='received_proposals')
    comment = models.TextField(verbose_name='Комментарий')
    status = models.CharField(verbose_name='Статус предложения', max_length=10, choices=STATUS_CHOICES, default='awaits')
    created_at = models.DateTimeField(verbose_name='Дата создания предложения', auto_now_add=True)

    def __str__(self):
        return f"Предложение: {self.ad_sender} -> {self.ad_receiver} ({self.status})"
