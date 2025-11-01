from django.contrib import admin
from django.utils.html import format_html
from apps.restaurant.models import *

# ================== PRODUCT ITEM ADMIN =====================
class ProductItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'main_category', 'sub_category', 'is_active',
        'is_available', 'stock_available', 'price', 'currency_symbol',
        'rating_avg', 'created_by'
    )
    list_filter = ('main_category', 'sub_category', 'is_active', 'is_available')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'rating_avg', 'created_at', 'updated_at')

# ================== OFFER ADMIN =====================
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'offer_type', 'discount_value', 'active', 'start_date', 'end_date')
    list_filter = ('offer_type', 'active')
    search_fields = ('name', 'description')

# ================== PRODUCT REVIEW ADMIN =====================
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name',)

# ================== CATEGORY ADMINS =====================
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'display_order')
    list_filter = ('is_active',)
    search_fields = ('name',)

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_category', 'name', 'is_active', 'display_order')
    list_filter = ('main_category', 'is_active')
    search_fields = ('name',)

# ================== REGISTER MODELS =====================
admin.site.register(MainCategory, MainCategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(ProductItem, ProductItemAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
