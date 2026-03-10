# from django.db.models.signals import post_delete, post_save, pre_save
# from .models import IssuedRecord, Book
# from django.dispatch import receiver

# @receiver(pre_save, sender=Book)
# def sync_initial_available_copies(sender, instance, **kwargs):
#     # If the book is being created for the first time
#     if instance._state.adding: 
#         instance.available_copies = instance.total_copies
#         print(f"DEBUG: Initial Sync - {instance.title} set to {instance.total_copies}")


# @receiver(pre_save, sender=IssuedRecord)
# def detect_returned(sender, instance, **kwargs):
#     # 1. If it's a new record (no PK), it can't be a "change" from None to Date
#     if not instance.pk:
#         instance._returned_changed = False
#         return

#     try:
#         # 2. Only fetch 'old' if the record exists in the DB
#         old = IssuedRecord.objects.get(pk=instance.pk)
#         instance._returned_changed = (
#             old.returned_date is None and instance.returned_date is not None
#         )
#     except IssuedRecord.DoesNotExist:
#         # 3. Fallback for safety
#         instance._returned_changed = False


# @receiver(post_save, sender=IssuedRecord)
# def update_book_cout_on_save(sender, instance, created, **kwargs):
#     if created:
#         print(f"DEBUG: New issue created for {instance.book.title}")
#         instance.book.issued_copy()
    
#     elif getattr(instance, '_returned_changed', False):
#         print(f"DEBUG: Return detected for {instance.book.title}")
#         instance.book.return_copy()


# @receiver(post_delete, sender=IssuedRecord)
# def update_book_count_on_delete(sender, instance, **kwargs):
    
#     if not instance.returned_date:
#         print(f"DEBUG: Return detected for {instance.book.title}")
#         instance.book.return_copy()
        

