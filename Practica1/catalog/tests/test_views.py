import datetime
from django.contrib.contenttypes.models import ContentType
# Obligatorio para asignar al usuario como prestatario
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from catalog.models import BookInstance, Book, Genre, Language
from django.utils import timezone
from django.test import TestCase
# Create your tests here.
from catalog.models import Author
from django.urls import reverse


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crear 13 autores para pruebas de paginación
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Christian %s' %
                                  author_num,
                                  last_name='Surname %s' % author_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)

        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        self.assertTrue(len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        resp = self.client.get(reverse('authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] is True)
        self.assertTrue(len(resp.context['author_list']) == 3)


class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # Crear dos usuarios
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(
            username='testuser2', password='12345')
        test_user2.save()

        # Crear un libro
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title', summary='My book summary',
            isbn='ABCDEFG', author=test_author, language=test_language)
        # Crear género como un paso posterior
        genre_objects_for_book = Genre.objects.all()
        # No se permite la asignación directa de tipos de muchos a muchos.
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Crea 30 objetos BookInstance
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = (timezone.now() +
                           datetime.timedelta(days=book_copy % 5))
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            BookInstance.objects.create(book=test_book,
                                        imprint='Unlikely Imprint, 2016',
                                        due_back=return_date,
                                        borrower=the_borrower,
                                        status=status)

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Comprueba que obtuvimos una respuesta "exitosa"
        self.assertEqual(resp.status_code, 200)

        # Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(
            resp, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)
        self.assertEqual(len(resp.context['bookinstance_list']), 0)

        # Ahora cambia todos los libros para que estén en préstamo
        get_ten_books = BookInstance.objects.all()[:10]

        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # Comprueba que ahora tenemos libros prestados en la lista
        resp = self.client.get(reverse('my-borrowed'))
        # Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        self.assertTrue('bookinstance_list' in resp.context)

        for bookitem in resp.context['bookinstance_list']:
            self.assertEqual(resp.context['user'],
                             bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):

        # Cambiar todos los libros para que estén en préstamo
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('my-borrowed'))

        # Comprobar que nuestro usuario tiene sesión iniciada
        self.assertEqual(str(resp.context['user']), 'testuser1')
        # Comprueba que obtuvimos una respuesta "éxito"
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(resp.context['bookinstance_list']), 10)

        last_date = 0
        for copy in resp.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)


class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        # Crear un usuario
        test_user1 = User.objects.create_user(
            username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(
            username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # Crear un libro
        test_author = Author.objects.create(
            first_name='John', last_name='Smith')
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title',
                                        summary='My book summary',
                                        isbn='ABCDEFG', author=test_author,
                                        language=test_language,)
        # Crear género como un paso posterior
        genre_objects_for_book = Genre.objects.all()
        # No se permite la asignación directa de tipos de muchos a muchos.
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        # Cree un objeto BookInstance para test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(
            book=test_book, imprint='Unlikely Imprint, 2016',
            due_back=return_date, borrower=test_user1, status='o')

        # Cree un objeto BookInstance para test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(
            book=test_book, imprint='Unlikely Imprint, 2016',
            due_back=return_date, borrower=test_user2, status='o')

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='12345')
        resp = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk, }))

        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        self.client.login(username='testuser2', password='12345')
        resp = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance2.pk, }))

        self.assertEqual(resp.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        self.client.login(username='testuser2', password='12345')
        resp = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk, }))

        self.assertEqual(resp.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        # ¡Es improbable que el UID coincida con nuestra instancia de libro!
        test_uid = uuid.uuid4()
        self.client.login(username='testuser2', password='12345')
        resp = self.client.get(
            reverse('renew-book-librarian', kwargs={'pk': test_uid, }))
        self.assertEqual(resp.status_code, 404)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='12345')
        resp = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        # Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        self.client.login(username='testuser2', password='12345')
        resp = self.client.get(
            reverse('renew-book-librarian',
                    kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = (datetime.date.today() +
                                  datetime.timedelta(weeks=3))
        self.assertEqual(
            resp.context['form'].initial['renewal_date'],
            date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.login(username='testuser2', password='12345')
        valid_date_in_future = (datetime.date.today()
                                + datetime.timedelta(weeks=2))
        resp = self.client.post(reverse('renew-book-librarian', kwargs={
                                'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': valid_date_in_future})
        self.assertRedirects(resp, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('renew-book-librarian', kwargs={
                                'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': date_in_past})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date',
                             'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = (datetime.date.today()
                                  + datetime.timedelta(weeks=5))
        resp = self.client.post(reverse('renew-book-librarian', kwargs={
                                'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': invalid_date_in_future})
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date',
                             'Invalid date - renewal more than 4 weeks ahead')


class AuthorCreateViewTest(TestCase):
    """Test case for the AuthorCreate view (Created as Challenge)."""

    def setUp(self):
        # Create a user
        test_user1 = User.objects.create_user(
            username='test_user1', password='some_password')

        test_user2 = User.objects.create_user(
            username='test_user2', password='some_password')

        content_typeAuthor = ContentType.objects.get_for_model(Author)
        permAddAuthor = Permission.objects.get(
            codename="add_author",
            content_type=content_typeAuthor,
        )

        test_user2.user_permissions.add(permAddAuthor)
        test_user1.save()
        test_user2.save()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('author-create'))
        # Revisar manualmente la redirección (no se puede usar assertRedirect
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(
            username='test_user1', password='some_password')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual(resp.status_code, 403)

    def test_logged_in_with_permission(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(reverse('author-create'))

        self.assertEqual(resp.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual(resp.status_code, 200)

        # Compruebe que usamos la plantilla correcta
        self.assertTemplateUsed(resp, 'catalog/author_form.html')

    def test_form_date_of_death_initially_set_to_expected_date(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.get(reverse('author-create'))
        self.assertEqual(resp.status_code, 200)

        expected_initial_date = datetime.date(2023, 11, 11)
        date = resp.context['form'].initial['date_of_death']
        date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
        self.assertEqual(date, expected_initial_date)

    def test_redirects_to_detail_view_on_success(self):
        self.client.login(
            username='test_user2', password='some_password')
        resp = self.client.post(reverse('author-create'),
                                {'first_name': 'Jacinto',
                                 'last_name': 'Montero'})
        # Manually check redirect because we don't know what author was created
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/catalog/author/'))
