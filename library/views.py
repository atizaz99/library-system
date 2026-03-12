from django.shortcuts import render
from .models import Author, Category, Book, IssuedRecord
from django.db.models import F, Case, When, Value, IntegerField, CharField, ExpressionWrapper, BooleanField
from django.db.models.functions import Coalesce, ExtractDay
from datetime import date
from django.db.models import F, Q, IntegerField, Count
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from core.helper import paginate_queryset
# Create your views here.

from .models import Book

def books(request):
    
    return render(request, 'library/librarylist.html')

def books_list_api(request):
    # 1. Base Query
    qs = Book.objects.select_related(
        'author'
    ).prefetch_related(
        'issues'
    ).annotate(
        issued_books = Count(
            'issues', 
            filter=Q(issues__returned_date__isnull = True)
        )
    ).annotate(
        calc_avaliable = Coalesce(
            F('total_copies')-F('issued_books'),
            F('total_copies'),
            output_field=IntegerField
        )
    ).values('id', 'title', 'isbn', 'author__name', 'total_copies', 'calc_avaliable' )

    paginated_data = paginate_queryset(qs, request, page_size=10)
    return JsonResponse(paginated_data)



