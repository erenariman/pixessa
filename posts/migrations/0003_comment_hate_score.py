# Generated by Django 5.2 on 2025-05-13 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_comment_is_offensive'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='hate_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
