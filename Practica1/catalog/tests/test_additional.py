"""
First Week Tests
Created by JAMI
EPS-UAM 2025
"""

from django.test import TestCase
from django.urls import reverse
from catalog.models import Book, BookInstance, Language, Genre, Author


class AdditionalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        try:
            from populate_catalog import populate
            populate()
        except ImportError:
            print('The module populate_catalog does not exist')
        except NameError:
            print('The function populate() does not exist or is not correct')
        except Exception:
            print('Something went wrong in the populate() function :-(')
            raise

    # Test for `date_of_death` label in the Author model
    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'death')

    # Test __str__ method of Author
    def test_author_str(self):
        author = Author.objects.get(id=1)
        self.assertEqual(str(author), 'King, Stephen')

    # Test __str__ method of Genre
    def test_genre_str(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(str(genre), 'Horror')

    # Test __str__ method of Book
    def test_book_str(self):
        book = Book.objects.get(id=1)
        self.assertEqual(str(book), 'The Shining')

    # Test __str__ method of Book
    def test_language_str(self):
        language = Language.objects.get(id=1)
        self.assertEqual(str(language), 'English')

    # Test __str__ method of BookInstance
    def test_book_instance_str(self):
        book_instance = BookInstance.objects.first()
        self.assertEqual(str(book_instance),
                         f'{book_instance.id} (The Shining)')
    """
    # Test get_absolute_url for Language
    def test_language_get_absolute_url(self):
        author = Language.objects.get(id=1)
        self.assertEqual(language.get_absolute_url(), reverse('language-detail', args=[str(language.id)]))

    # Test get_absolute_url for Author
    def test_author_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEqual(author.get_absolute_url(), reverse('author-detail', args=[str(author.id)]))

    # Test get_absolute_url for Book
    def test_book_get_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEqual(book.get_absolute_url(), reverse('book-detail', args=[str(book.id)]))

    # Test get_absolute_url for Genre
    def test_genre_get_absolute_url(self):
        genre = Genre.objects.get(id=1)
        self.assertEqual(genre.get_absolute_url(), reverse('genre-detail', args=[str(genre.id)]))

    """
