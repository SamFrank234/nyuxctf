# Generated by Django 4.1.4 on 2023-01-07 17:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('worldcup', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='team',
            name='matches',
            field=models.ManyToManyField(blank=True, to='worldcup.match'),
        ),
    ]
