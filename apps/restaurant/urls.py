from django.urls import path
from apps.restaurant.views import *

urlpatterns = [
    # ================== PRODUCT ITEMS ==================
    path('product-items/', product_items_list_create, name='product_items_list_create'),
    path('product-items/<int:id>/', product_item_detail, name='product_item_detail'),
    path('product-items/update/<int:id>/', product_item_update, name='product_item_update'),
    path('product-items/delete/<int:id>/', product_item_delete, name='product_item_delete'),
    # ================== MAIN CATEGORIES ==================
    path('main-categories/', main_category_list, name='main_category_list'),
    path('main-categories/create/', main_category_create, name='main_category_create'),
    path('main-categories/<int:id>/', main_category_detail, name='main_category_detail'),
    path('main-categories/update/<int:id>/', main_category_update, name='main_category_update'),
    path('main-categories/delete/<int:id>/', main_category_delete, name='main_category_delete'),
    # ================== SUB CATEGORIES ==================
    path('sub-categories/', sub_category_list, name='sub_category_list'),
    path('sub-categories/create/', sub_category_create, name='sub_category_create'),
    path('sub-categories/<int:id>/', sub_category_detail, name='sub_category_detail'),
    path('sub-categories/update/<int:id>/', sub_category_update, name='sub_category_update'),
    path('sub-categories/delete/<int:id>/', sub_category_delete, name='sub_category_delete'),
    # ================== PRODUCT IMAGES ==================
    path('product-images/', product_image_list, name='product_image_list'),
    path('product-images/create/', product_image_create, name='product_image_create'),
    path('product-images/<int:id>/', product_image_detail, name='product_image_detail'),
    path('product-images/delete/<int:id>/', product_image_delete, name='product_image_delete'),
    # ================== OFFERS ==================
    path('offers/', offer_list, name='offer_list'),
    path('offers/create/', offer_create, name='offer_create'),
    path('offers/<int:id>/', offer_detail, name='offer_detail'),
    path('offers/update/<int:id>/', offer_update, name='offer_update'),
    path('offers/delete/<int:id>/', offer_delete, name='offer_delete'),
    # ================== PRODUCT REVIEWS ==================
    path('product-reviews/', product_review_list, name='product_review_list'),
    path('product-reviews/create/', product_review_create, name='product_review_create'),
    path('product-reviews/<int:id>/', product_review_detail, name='product_review_detail'),
    path('product-reviews/delete/<int:id>/', product_review_delete, name='product_review_delete'),
]
