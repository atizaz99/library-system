from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# paination helper defualt 10 record but show by also in each view 

def paginate_queryset(queryset, request, page_size):
    page_numer = request.GET.get('page', 1)
    
    page_size = page_size if page_size else 10 
    paginator = Paginator(queryset, page_size)

    try:
        page_obj = paginator.page(page_numer)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return {
        'items': list(page_obj.object_list),
        'meta': {
           'total': paginator.count,
           'total_pages': paginator.num_pages,
           'current_page': page_obj.number,
           'has_next': page_obj.has_next(),
           'has_previous': page_obj.has_previous(),
           'start_index': page_obj.start_index(),
           'end_index': page_obj.end_index(),
           'page_size': int(page_size)

        }
    }