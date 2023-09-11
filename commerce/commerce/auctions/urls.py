from django.urls import path

from . import views

app_name = 'auctions'
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_auction", views.create_auction, name="create_auction"),
    path("your_listing", views.your_listing, name="your_listing"),
    path("edit_listing/<int:pk>", views.edit_listing, name='edit_listing'),
    path('delete_auction/<int:pk>', views.delete_auction, name='delete_auction'),
    path("auction_detail/<int:pk>", views.auction_detail, name="auction_detail"),
    path('place_bid/<int:pk>', views.place_bid, name='place_bid'),
    path('watchlist/<int:pk>', views.watchlist, name='watchlist'),
    path('watchlist_view', views.watchlist_view, name='watchlist_view'),

    path('watchlist/<int:pk>', views.remove_listing, name='remove_listing'),

    path('my_listings/<int:user_id>/', views.my_listings, name='my_listings'),
    path('my_listings/<int:user_id>/<int:listing_id>/', views.my_listings, name='my_listings_with_listing_id'),



]







