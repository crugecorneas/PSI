"""
First Week Tests
Created by JAMI
EPS-UAM 2025
"""

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from catalog.models import Book, BookInstance, Language, Genre, Author
from unittest.mock import patch


class AdditionalTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        try:
            Author.objects.create(id=100, first_name='test', last_name='test')
            book = Book.objects.create(id=100, title='test')
            Genre.objects.create(id=100, name='nothing')
            Language.objects.create(id=100, name='Invented')
            BookInstance.objects.create(id=100, book=book)
        except ImportError:
            print('The module populate_catalog does not exist')
        except NameError:
            print('The function populate() does not exist or is not correct')
        except Exception:
            print('Something went wrong in the populate() function :-(')
            raise

    def test_date_of_death_label(self):
        author = Author.objects.get(id=100)
        field_label = author._meta.get_field('date_of_death').verbose_name
        self.assertEqual(field_label, 'died')

    def test_author_str(self):
        author = Author.objects.get(id=100)
        self.assertEqual(str(author), 'test, test')

    def test_genre_str(self):
        genre = Genre.objects.get(id=100)
        self.assertEqual(str(genre), 'nothing')

    def test_book_str(self):
        book = Book.objects.get(id=100)
        self.assertEqual(str(book), 'test')

    def test_language_str(self):
        language = Language.objects.get(id=100)
        self.assertEqual(str(language), 'Invented')

    def test_book_instance_str(self):
        book_instance = BookInstance.objects.first()
        self.assertEqual(str(book_instance),
                         f'{book_instance.id} (test)')

    def test_author_get_absolute_url(self):
        author = Author.objects.get(id=100)
        self.assertEqual(author.get_absolute_url(), reverse(
            'author-detail', args=[str(author.id)]))

    def test_book_get_absolute_url(self):
        book = Book.objects.get(id=100)
        self.assertEqual(book.get_absolute_url(), reverse(
            'book-detail', args=[str(book.id)]))

    def test_display_genre(self):
        book = Book.objects.get(id=100)
        genre1 = Genre.objects.get(id=100)

        book.genre.add(genre1)
        self.assertEqual(book.display_genre(), 'nothing')


""" def test_language_get_absolute_url(self):
        language = Language.objects.get(id=100)
        self.assertEqual(language.get_absolute_url(), reverse(
            'language-detail', args=[str(language.id)]))

    def test_genre_get_absolute_url(self):
        genre = Genre.objects.get(id=100)
        self.assertEqual(genre.get_absolute_url(), reverse(
            'genre-detail', args=[str(genre.id)]))"""


class BookCreateViewTest(TestCase):

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username='test_user1', password='some_password')

        test_user2 = User.objects.create_user(
            username='test_user2', password='some_password')

        ContentType.objects.get_for_model(Book)
        permission = Permission.objects.get(name='Set book as returned')

        test_user2.user_permissions.add(permission)
        test_user1.save()
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('book-create'))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(
            username='test_user1', password='some_password')
        resp = self.client.get(reverse('book-create'))
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_with_permission(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(reverse('book-create'))
        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(reverse('book-create'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/book_form.html')

    def test_book_create_invalid_isbn(self):
        self.client.login(
            username='test_user2', password='some_password')
        test_author = Author.objects.create(
            id=134, first_name='Johdana', last_name='Smithdad')
        test_genre = Genre.objects.create(id=91, name='Fantasy')
        test_language = Language.objects.create(id=128, name='English')
        resp = self.client.post(reverse('book-create'), {
            'title': 'Test Book',
            'author': test_author.id,
            'summary': 'Summary',
            'isbn': '12345',  # ISBN inválido
            'language': test_language.id,
            'genre': test_genre.id,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'isbn',
                             'El ISBN debe tener exactamente 13 caracteres.')

    def test_book_create_valid_isbn(self):
        self.client.login(
            username='test_user2', password='some_password')
        Author.objects.create(
            id=124, first_name='Johdan', last_name='Smithdad')
        Genre.objects.create(name='Fantasy')
        Language.objects.create(name='English')
        """"
        # Hacer la solicitud POST con ISBN válido
        resp = self.client.post(reverse('book-create'), {
            'title': 'Test Book',
            'author': test_author.id,
            'summary': 'Summary',
            'isbn': '9781234567890',  # ISBN válido
            'language': test_language.id,
            'genre': test_genre.id,
        })"""

        """self.assertEqual(resp.status_code, 302)
        self.assertTrue(Book.objects.filter(isbn='9781234567890').exists())"""


class AuthorDeleteViewTest(TestCase):

    def setUp(self):
        test_user1 = User.objects.create_user(
            username='test_user1', password='some_password')

        test_user2 = User.objects.create_user(
            username='test_user2', password='some_password')
        self.author = Author.objects.create(id=192, first_name="Test Author")

        content_typeAuthor = ContentType.objects.get_for_model(Author)
        permDeleteAuthor = Permission.objects.get(
            codename="delete_author",
            content_type=content_typeAuthor,
        )

        test_user2.user_permissions.add(permDeleteAuthor)
        test_user1.save()
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(
            reverse('author-delete', kwargs={'pk': self.author.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(
            username='test_user1', password='some_password')
        resp = self.client.get(
            reverse('author-delete', kwargs={'pk': self.author.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_with_permission(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(
            reverse('author-delete', kwargs={'pk': self.author.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(
            reverse('author-delete', kwargs={'pk': self.author.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/author_confirm_delete.html')

    def test_author_delete_success(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.post(
            reverse('author-delete', kwargs={'pk': self.author.pk}))
        self.assertRedirects(resp, reverse('authors'))
        self.assertFalse(Author.objects.filter(pk=self.author.pk).exists())
        Author.objects.filter(id=192).delete()

    def test_author_delete_failure(self):
        self.client.login(
            username='test_user2', password='some_password')
        author = Author.objects.create(
            id=100, first_name='John', last_name='Smith')

        with patch.object(Author,
                          'delete',
                          side_effect=Exception("Simulated error")):
            resp = self.client.post(
                reverse('author-delete', kwargs={'pk': author.pk}))
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(resp, reverse(
                'author-delete', kwargs={'pk': author.pk}))


class BookDeleteViewTest(TestCase):

    def setUp(self):
        # Crear usuarios
        test_user1 = User.objects.create_user(
            username='test_user1', password='some_password')

        test_user2 = User.objects.create_user(
            username='test_user2', password='some_password')
        self.book = Book.objects.create(id=3, title='testing')
        content_typeBook = ContentType.objects.get_for_model(Book)
        permDeleteBook = Permission.objects.get(
            codename="delete_book",
            content_type=content_typeBook,
        )

        test_user2.user_permissions.add(permDeleteBook)
        test_user1.save()
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(
            reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(
            username='test_user1', password='some_password')
        resp = self.client.get(
            reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_with_permission(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(
            reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(
            reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/book_confirm_delete.html')

    def test_book_delete_failure(self):
        self.client.login(
            username='test_user2', password='some_password')
        test_author = Author.objects.create(id=201,
                                            first_name='Johna',
                                            last_name='Smithd')
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(id=192,
                                        title='Book Title',
                                        summary='My book summary',
                                        isbn='ABCDEFG', author=test_author,
                                        language=test_language)
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        with patch.object(Book, 'delete',
                          side_effect=Exception("Simulated error")):
            resp = self.client.post(
                reverse('book-delete', kwargs={'pk': test_book.pk}))
            self.assertEqual(resp.status_code, 302)
            self.assertRedirects(resp, reverse(
                'book-delete', kwargs={'pk': test_book.pk}))
        self.client.post(reverse('book-delete', kwargs={'pk': self.book.pk}))

    def test_book_delete_success(self):

        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.post(
            reverse('book-delete', kwargs={'pk': self.book.pk}))
        self.assertRedirects(resp, reverse('books'))
        self.assertFalse(Book.objects.filter(pk=self.book.pk).exists())
