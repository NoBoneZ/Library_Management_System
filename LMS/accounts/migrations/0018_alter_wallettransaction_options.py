# Generated by Django 4.1.1 on 2022-09-25 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_wallettransaction_balance_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wallettransaction',
            options={'ordering': ('-date_occurred',)},
        ),
    ]
