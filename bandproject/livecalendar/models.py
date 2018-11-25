from django.db import models

# Create your models here.
class Band(models.Model):
    name = models.CharField('バンド名', max_length = 50)

    def __str__(self):
        return self.name


class Live(models.Model):
    """ライブ情報"""
    date = models.DateField('日程')
    title = models.CharField('企画名', max_length = 50)
    place = models.CharField('ライブハウス', max_length = 30)
    band = models.ManyToManyField(Band, verbose_name='出演バンド',blank=True)
    open = models.TimeField('OPEN',blank=True,null=True)
    start = models.TimeField('START',blank=True,null=True)
    door = models.IntegerField('当日料金',blank=True,null=True)
    adv = models.IntegerField('前売料金',blank=True,null=True)

    def __str__(self):
        return self.title
