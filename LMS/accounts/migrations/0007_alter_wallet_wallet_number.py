# Generated by Django 4.1.1 on 2022-09-23 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_wallet_outstanding_debts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallet',
            name='wallet_number',
            field=models.CharField(max_length=11, null=True, unique=True),
        ),
    ]