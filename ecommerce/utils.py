from .models import Product


def sorted_queryset(order_by, query):
    queryset = Product.objects.filter(query).order_by('-updated_on').distinct()
    if order_by == 'highest_price':
        queryset = Product.objects.filter(query).order_by('-productdetail__price').distinct()
    if order_by == 'lowest_price':
        queryset = Product.objects.filter(query).order_by('productdetail__price').distinct()
    if order_by == 'highest_discount':
        queryset = Product.objects.filter(query).order_by('-productdetail__discount').distinct()
    if order_by == 'lowest_discount':
        queryset = Product.objects.filter(query).order_by('productdetail__discount').distinct()
    if order_by == 'highest_rating':
        queryset = Product.objects.filter(query).order_by('-productreview__rating').distinct()
    if order_by == 'lowest_rating':
        queryset = Product.objects.filter(query).order_by('productreview__rating').distinct()
    return queryset
