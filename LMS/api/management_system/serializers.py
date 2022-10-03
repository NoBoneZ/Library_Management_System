from rest_framework import serializers

from management_system.models import Book, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("name",)


class BookSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ("title", "authors", "genre", "isbn13", "num_of_pages")
