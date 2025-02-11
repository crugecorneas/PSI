import uuid  # Required for unique book instances
# Returns lower cased value of field
from django.db.models.functions import Lower
# Constrains fields to unique values
from django.db.models import UniqueConstraint
# Used in get_absolute_url() to get URL for specified ID
from django.urls import reverse
from django.db import models
from django.conf import settings
from datetime import date



class Language(models.Model):
    """A typical class defining a model, derived from the Model class."""

    # Fields
    name = models.CharField(
        max_length=20, help_text='Enter a language name'
    )
    # …

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def get_absolute_url(self):
        """Returns the URL to access a particular instance of MyModelName."""
        return reverse(
            'language-detail', args=[str(self.id)]
        )

    def __str__(self):
        """Representing the MyModelName object (in Admin site etc)"""
        return self.name


class Genre(models.Model):
    """Model representing a book genre."""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction, French...)"
    )

    def __str__(self):
        """String for representing the Model object."""
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a particular genre instance."""
        return reverse('genre-detail', args=[str(self.id)])

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message=(
                    "Genre already exists (case insensitive match)"
                )
            ),
        ]


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    language = models.ForeignKey(
        'Language', on_delete=models.RESTRICT, null=True
    )
    author = models.ForeignKey(
        'Author', on_delete=models.RESTRICT, null=True
    )  # Foreign Key used because book can only have one author, but authors
    # can have multiple books.
    # Author as a string rather than object because it hasn't been declared yet
    # in file.

    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        'ISBN', max_length=13, unique=True,
        help_text=(
            '13 Character <a href="https://www.isbn-international.org/content/'
            'what-isbn">ISBN number</a>'
        )
    )

    # ManyToManyField used cause genre can contain many books. Books can cover
    # many genres. Genre class has already been defined so we can specify the
    # object above.
    genre = models.ManyToManyField(
        Genre, help_text="Select a genre for this book"
    )

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access a detail record for this book."""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """
        Creates a string for the Genre. This is required to display genre in Admin.
        """
        return ', '.join([ genre.name for genre in self.genre.all()[:3] ])
    display_genre.short_description = 'Genre'

    class Meta:
        ordering = ['title']


class BookInstance(models.Model):

    # Model representing a specific copy of a book
    # (i.e. that can be borrowed from the library)
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4,
        help_text="Unique ID for this particular book across whole library"
    )
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)


    def __str__(self):
        """String for representing the Model object."""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """
    Modelo que representa un autor
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField('birth', null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        Retorna la url para acceder a una instancia particular de un autor.
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """
        String para representar el Objeto Modelo
        """
        return '%s, %s' % (self.last_name, self.first_name)
