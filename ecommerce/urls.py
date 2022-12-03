from django.urls import path
from ecommerce import views

app_name = "ecommerce"

urlpatterns = [
    path("", views.MallLandPageView.as_view(), name="mall-land-page"),
    path("categories/", views.CategoriesView.as_view(), name="categories"),
    path("categories/<int:pk>/", views.CategoriesView.as_view(), name="categories-detail"),
    path("top-selling/", views.TopSellingProductsView.as_view(), name="top-selling"),
    path("recommended-products/", views.RecommendedProductView.as_view(), name="recommended-products"),
    path("filtered-search/", views.FilteredSearchView.as_view(), name="product-filter"),

    # CART
    path("cart/", views.CartProductOperationsView.as_view(), name="add-to-cart"),
    path("cart/<str:id>/", views.CartProductOperationsView.as_view(), name="cart-products"),


    # Wishlist
    path("wishlist/", views.ProductWishlistView.as_view(), name="wishlist"),    # GET, POST
    path("wishlist/<int:id>/", views.RetrieveDeleteWishlistView.as_view(), name="wishlist-detail"),

    # Products
    path("product/", views.ProductView.as_view(), name="product"),
    path("product/<int:pk>/", views.ProductView.as_view(), name="product-detail"),

    # Order
    path("checkout/", views.ProductCheckoutView.as_view(), name="checkout"),
    path("track-order", views.TrackOrderAPIView.as_view(), name="track-order"),
    path("order/", views.OrderAPIView.as_view(), name="orders"),
    path("order/<int:pk>/", views.OrderAPIView.as_view(), name="order-detail"),
    path("order/return/<int:pk>/", views.OrderReturnView.as_view(), name="return-order-detail"),
    path("order/return/", views.OrderReturnView.as_view(), name="return-all"),

    # Customer Dashboard
    path("dashboard/", views.CustomerDashboardView.as_view(), name="customer-dashboard"),

    # Product Review
    path("review/", views.ProductReviewAPIView.as_view(), name="review"),

    # Name Enquiry
    path("name-enquiry/", views.NameEnquiryAPIView.as_view(), name="name-enquiry"),

]
