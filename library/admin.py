from django.contrib import admin
from .models import Author, Category, Book, IssuedRecord

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'is_deleted')
    search_fields = ('name',)
@admin.register(Category)
class Category(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )
from django.db.models import F, Q, IntegerField, Count
from django.db.models.functions import Coalesce

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'author', 'total_copies', 'available_count')
    list_filter = ('category', 'author')
    search_fields = ('title', 'isbn')

    

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            # 1. SQl count of issue 
            active_issues = Count(
                'issues',
                filter = Q(issues__returned_date__isnull= True)
            )
        ).annotate(
            # 2. SQL Subtraction: Total - Active
            calc_avalible = Coalesce(
                F('total_copies')-F('active_issues'),
                F('total_copies'),
                output_field=IntegerField()
            )

        )
    

    @admin.display(description='Available')
    def available_count(self, obj):
        return obj.calc_avalible

from django.contrib import admin
from django.db.models import F, Case, When, Value, IntegerField, CharField, ExpressionWrapper, BooleanField
from django.db.models.functions import Coalesce, ExtractDay
from datetime import date
from .models import IssuedRecord

@admin.register(IssuedRecord)
class IssuedRecordAdmin(admin.ModelAdmin):
    # We use the annotated field names here to make them sortable
    list_display = ('book', 'user', 'due_date', 'admin_fine', 'admin_overdue', 'admin_status')
    list_filter = ('due_date', 'issued_date')
    readonly_fields = ('admin_fine', 'admin_overdue', 'admin_status', 'issued_date')
    search_fields = ('user__email', 'book__title')

    def get_queryset(self, request):
        """
        Optimised SQL Logic: Calculates all properties in ONE database query.
        This allows the admin to SORT by Fine or Status.
        """
        today = date.today()
        queryset = super().get_queryset(request)
        
        return queryset.annotate(
            # 1. Logic for Fine calculation
            effective_date=Coalesce(F('returned_date'), Value(today)),
        ).annotate(
            delay_days=ExpressionWrapper(
                ExtractDay(F('effective_date') - F('due_date')),
                output_field=IntegerField()
            )
        ).annotate(
            # Annotated Fine
            sql_fine=Case(
                When(delay_days__gt=0, then=F('delay_days') * 10),
                default=Value(0),
                output_field=IntegerField()
            ),
            # Annotated Overdue Status (Boolean)
            sql_overdue=Case(
                When(returned_date__isnull=True, due_date__lt=today, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            # Annotated Professional Status Label
            sql_status=Case(
                When(returned_date__isnull=True, then=Value('Still Borrowed')),
                When(returned_date__lte=F('due_date'), then=Value('On-time Returned')),
                default=Value('Late Returned'),
                output_field=CharField()
            )
        )

    # --- Display Methods for Admin Columns ---

    @admin.display(description='Fine (Rs.)', ordering='sql_fine')
    def admin_fine(self, obj):
        # Fallback to model property if annotation isn't loaded
        val = getattr(obj, 'sql_fine', obj.calculate_fine)
        return f"Rs. {val}"

    @admin.display(description='Is Overdue?', ordering='sql_overdue', boolean=True)
    def admin_overdue(self, obj):
        return getattr(obj, 'sql_overdue', obj.is_overdue)

    @admin.display(description='Return Status', ordering='sql_status')
    def admin_status(self, obj):
        return getattr(obj, 'sql_status', obj.timely_returned)


#admin login user atizazhussain@gmail.com
# password: 1234
