from django.db import models
from core.models import BaseModel
from django.conf import settings
from datetime import date, timedelta
from django.db.models import F

# Create your models here.

#1. Author Table 
class Author(BaseModel):
    name = models.CharField(verbose_name='Name', db_index=True, max_length=100)
    bio = models.TextField(verbose_name= 'Author Biography', null=True, blank=True)

    def __str__(self):
        return self.name
    
# 2 Category
class Category(BaseModel):
    name = models.CharField(verbose_name='Name', unique=True, max_length=100)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name
    

# 3 Book 
class Book(BaseModel):
    title = models.CharField(verbose_name='Title', db_index=True, max_length=255)
    isbn = models.CharField(verbose_name='ISBN', max_length=13, unique=True)
    author = models.ForeignKey(Author, related_name='books', verbose_name='Author', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='books', verbose_name='Category', on_delete=models.SET_NULL, null=True, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    # available_copies = models.PositiveIntegerField(editable=False)

    # def issued_copy(self):
    #     if self.available_copies >0:
    #         self.available_copies = F('available_copies') -1 
    #         self.save(update_fields=['available_copies'])
    #         self.refresh_from_db()

    # def return_copy(self):
    #     if self.available_copies < self.total_copies:
    #         self.available_copies = F('available_copies') + 1
    #         self.save(update_fields=['available_copies'])
    #         self.refresh_from_db()

    def __str__(self):
        return f'{self.title} ({self.isbn})'
    

# 4. Issue Record (Links User to Book - The Transaction)
class IssuedRecord(BaseModel):
    book = models.ForeignKey(Book, db_index=True, verbose_name='Book', related_name='issues', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, db_index=True, verbose_name='User', related_name='borrowed_books', on_delete=models.CASCADE)
    issued_date = models.DateField(auto_now_add=True, verbose_name='Issued Date')
    due_date = models.DateField(verbose_name='Due Date', blank=True)
    returned_date = models.DateField(verbose_name='Returned Date', null=True, blank=True)
    

    class Meta:
        verbose_name = 'Issued Record'
        verbose_name_plural = 'Issued Records'


    
    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = date.today() + timedelta(days=14)
        super().save(*args, **kwargs)
    
    def __str__(self):
        name = self.user.get_full_name() 
        return f'{self.book.title} issued to { name if name else self.user.email}'
    
    @property
    def calculate_fine(self):
        if  not self.due_date:
            return 0
        if self.returned_date:
            if self.returned_date > self.due_date:
                delay = (self.returned_date-self.due_date).days
                return delay * 10
            return 0 
        
        # if not yet returned, check against today's date
        today = date.today()
        if today > self.due_date:
            delay = (today - self.due_date).days
            return delay * 10
        return 0
    @property
    def is_overdue(self):
        if not self.due_date or self.returned_date:
            return False
        return date.today() > self.due_date
    @property
    def timely_returned(self):
        if not self.returned_date:
            return 'Still Borrowed' # More professional
        return 'On-time Returned' if self.returned_date <= self.due_date else 'Late Returned'
        
        
    
    


        
    



