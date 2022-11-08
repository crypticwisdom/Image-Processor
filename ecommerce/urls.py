from django.urls import path
from ecommerce import views

app_name = "ecommerce"

urlpatterns = [
    path("", views.MallLandPageView.as_view(), name="mall-land-page"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("top-selling/", views.TopSellingProductsView.as_view(), name="top-selling"),
    path("recommended-products/", views.RecommendedProductView.as_view(), name="recommended-products"),
    path("filtered-search/", views.FilteredSearchView.as_view(), name="product-filter"),

    # CART
    path("cart-operation/", views.CartProductOperationsView.as_view(), name="add-to-cart"),
    path("cart-product/<str:id>", views.CartProductView.as_view(), name="cart-products"),


    # Wishlist
    path("wishlist/", views.ProductWishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:id>/", views.RetrieveDeleteWishlistView.as_view(), name="wishlist-detail"),

    # Products
    path("product/", views.ProductView.as_view(), name="product"),
    path("product/<int:pk>/", views.ProductView.as_view(), name="product-detail"),

    # Order
    path("checkout/", views.ProductCheckoutView.as_view(), name="checkout"),
    path("order/", views.OrderAPIView.as_view(), name="orders"),
    path("order/<int:pk>/", views.OrderAPIView.as_view(), name="order-detail"),

]
