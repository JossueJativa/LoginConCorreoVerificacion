# Generated by Django 4.2.2 on 2023-07-11 22:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LoginUser', '0005_alter_user_genero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='genero',
            field=models.CharField(default='M', max_length=1),
        ),
    ]