# Generated by Django 2.0.5 on 2018-11-21 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('livecalendar', '0003_auto_20181121_2153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='live',
            name='band',
            field=models.ManyToManyField(blank=True, to='livecalendar.Band', verbose_name='出演バンド'),
        ),
    ]