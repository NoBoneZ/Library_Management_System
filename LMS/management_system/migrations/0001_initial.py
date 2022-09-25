# Generated by Django 4.1.1 on 2022-09-22 18:49

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('bookID', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=500, null=True)),
                ('authors', models.TextField(help_text="End Every Name with a \\, e.g, Adekunle, Ciroma Chukwuma/ , the main author's name should be the first")),
                ('thumbnail', models.ImageField(blank=True, upload_to='book_thumbnail')),
                ('isbn', models.CharField(blank=True, max_length=10, null=True)),
                ('isbn13', models.CharField(max_length=13)),
                ('average_rating', models.DecimalField(decimal_places=2, default=0.0, max_digits=3, null=True, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('ratings_count', models.IntegerField(default=0, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('language_code', models.CharField(max_length=7, null=True)),
                ('num_of_pages', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('publisher', models.CharField(blank=True, max_length=500, null=True)),
                ('publication_date', models.DateField(blank=True, null=True)),
                ('quantity', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
            },
        ),
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='BorrowedBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_borrowed', models.DateTimeField(auto_now_add=True)),
                ('date_to_be_returned', models.DateField(null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('book', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management_system.book')),
                ('borrower', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(to='management_system.genre'),
        ),
    ]
