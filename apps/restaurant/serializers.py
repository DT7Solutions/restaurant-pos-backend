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
from rest_framework import serializers
from .models import ProductItem

class ProductItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)

    class Meta:
        model = ProductItem
        fields = '__all__'

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def update(self, instance, validated_data):
        if 'image' in validated_data:
            image = validated_data.get('image')
            if image in [None, '', 'null']:
                if instance.image:
                    instance.image.delete(save=False)
                instance.image = None
            else:
                instance.image = image

        return super().update(instance, validated_data)

# ============================================================
# PRODUCT REVIEW SERIALIZER
# ============================================================
class ProductReviewSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductReview
        fields = '__all__'
        read_only_fields = ['id', 'product_name', 'created_at']
