# Generated by Django 4.1.1 on 2022-09-26 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management_system', '0018_renewalrequest_new_date_of_return'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewalrequest',
            name='new_date_of_return',
            field=models.DateField(null=True),
        ),
    ]