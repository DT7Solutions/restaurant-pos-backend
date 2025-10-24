from django.contrib import admin
from django.utils.html import format_html
from apps.restaurant.models import *

# ================== PRODUCT IMAGE INLINE =====================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('display_image',)
    fields = ('image', 'alt_text', 'display_order', 'is_main_image', 'display_image')

    def display_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="40" style="object-fit:cover; border-radius:5px;" />',
                obj.image.url
            )
        return "No Image"
    display_image.short_description = "Preview"

# ================== PRODUCT ITEM ADMIN =====================
class ProductItemAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'main_category', 'sub_category', 'is_active',
        'is_available', 'stock_available', 'price', 'currency_symbol',
        'rating_avg', 'created_by'
    )
    list_filter = ('main_category', 'sub_category', 'is_active', 'is_available', 'stock_available')
    search_fields = ('name', 'description')
    readonly_fields = ('slug', 'rating_avg', 'created_at', 'updated_at')
    inlines = [ProductImageInline]
    fields = (
        'main_category', 'sub_category', 'name', 'slug', 'description', 'prepare_time',
        'variant_type', 'quantity_value', 'quantity_unit', 
        'price', 'currency_symbol',
        'tax_percentage', 'stock_available', 'is_available', 'is_active',
        'max_order_quantity', 'offers', 'customizations',
        'created_by', 'created_at', 'updated_at'
    )

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
admin.site.register(ProductImage)
admin.site.register(Offer, OfferAdmin)
admin.site.register(ProductReview, ProductReviewAdmin)
