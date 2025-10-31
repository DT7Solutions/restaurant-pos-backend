from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

# ============================================================
# USER SERIALIZER (Basic)
# ============================================================
User = get_user_model()
class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

# ============================================================
# MAIN CATEGORY SERIALIZER
# ============================================================
class MainCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MainCategory
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

# ============================================================
# SUB CATEGORY SERIALIZER
# ============================================================
class SubCategorySerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)
    class Meta:
        model = SubCategory
        fields = '__all__'
        read_only_fields = ['id']

# ============================================================
# OFFER SERIALIZER
# ============================================================
class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = '__all__'
        read_only_fields = ['id']

# ============================================================
# PRODUCT ITEM SERIALIZER
# ============================================================
class ProductItemSerializer(serializers.ModelSerializer):
    main_image = serializers.SerializerMethodField()
    # main_category = MainCategorySerializer(read_only=True)
    # sub_category = SubCategorySerializer(read_only=True)
    # created_by = UserBasicSerializer(read_only=True)
    # offers_details = OfferSerializer(source='offers', many=True, read_only=True)

    # main_category_id = serializers.PrimaryKeyRelatedField(
    #     queryset=MainCategory.objects.all(),
    #     source='main_category',
    #     write_only=True,
    #     help_text="Select the main category ID"
    # )
    # sub_category_id = serializers.PrimaryKeyRelatedField(
    #     queryset=SubCategory.objects.all(),
    #     source='sub_category',
    #     write_only=True,
    #     help_text="Select the sub category ID"
    # )
    # offers = serializers.PrimaryKeyRelatedField(
    #     queryset=Offer.objects.all(),
    #     many=True,
    #     required=False,
    #     write_only=True,
    #     help_text="Select applicable offer IDs"
    # )
    
    def get_main_image(self, obj):
        return obj.main_image

    class Meta:
        model = ProductItem
        fields = '__all__'
        read_only_fields = [ 'id', 'slug', 'created_by', 'created_at', 'updated_at', 'main_category_id', 'sub_category_id', 'offers_details' ]

# ============================================================
# PRODUCT IMAGE SERIALIZER
# ============================================================
class ProductImageSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductImage
        fields = '__all__'
        read_only_fields = ['id', 'product_name']

# ============================================================
# PRODUCT REVIEW SERIALIZER
# ============================================================
class ProductReviewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ['id', 'product_name', 'created_at']
