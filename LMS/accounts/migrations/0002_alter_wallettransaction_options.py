# Generated by Django 4.1.1 on 2022-09-27 13:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='wallettransaction',
            options={'ordering': ('-date_occurred', 'wallet')},
        ),
    ]
