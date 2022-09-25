# Generated by Django 4.1.1 on 2022-09-23 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management_system', '0008_renewalrequest'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='renewalrequest',
            name='book',
        ),
        migrations.RemoveField(
            model_name='renewalrequest',
            name='name',
        ),
        migrations.AddField(
            model_name='renewalrequest',
            name='borrowed_book',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management_system.borrowedbook'),
        ),
        migrations.CreateModel(
            name='BookReturn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_approved', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('borrowed_book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management_system.borrowedbook')),
            ],
        ),
    ]