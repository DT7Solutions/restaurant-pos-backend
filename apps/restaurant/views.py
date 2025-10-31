from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, parsers, generics, permissions
from .models import *
from .serializers import *

# ============================================================
# PRODUCT CHOICES
# ============================================================
@api_view(['GET'])
def get_product_choices(request):
    try:
        variant_choices = [
            {"value": v[0], "label": v[1]} for v in ProductItem._meta.get_field('variant_type').choices
        ]
        unit_choices = [
            {"value": v[0], "label": v[1]} for v in ProductItem._meta.get_field('quantity_unit').choices
        ]
        currency_choices = [
            {"value": v[0], "label": v[1]} for v in ProductItem._meta.get_field('currency_symbol').choices
        ]

        return Response({
            "variant_choices": variant_choices,
            "unit_choices": unit_choices,
            "currency_choices": currency_choices,
        })
    except Exception as e:
        print("Error in get_product_choices:", e)
        return Response({"error": str(e)}, status=500)

# ============================================================
# PRODUCT ITEMS
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_items_list_create(request):
    if request.method == 'GET':
        products = ProductItem.objects.all().select_related('main_category', 'sub_category').prefetch_related('offers', 'images')
        serializer = ProductItemSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = ProductItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response({"message": "Product created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_item_detail(request, id):
    product = get_object_or_404(ProductItem, id=id)
    serializer = ProductItemSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def product_item_update(request, id):
    product = get_object_or_404(ProductItem, id=id)
    serializer = ProductItemSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_item_delete(request, id):
    product = get_object_or_404(ProductItem, id=id)
    product.delete()
    return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# MAIN CATEGORY
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def main_category_list_create(request):
    if request.method == 'GET':
        categories = MainCategory.objects.all()
        serializer = MainCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = MainCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response( {"message": "Main category created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED )
        return Response( {"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST )

@api_view(['GET'])
def main_category_detail(request, id):
    category = get_object_or_404(MainCategory, id=id)
    serializer = MainCategorySerializer(category)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def main_category_update(request, id):
    category = get_object_or_404(MainCategory, id=id)
    serializer = MainCategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Main category updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def main_category_delete(request, id):
    category = get_object_or_404(MainCategory, id=id)
    category.delete()
    return Response({"message": "Main category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# SUB CATEGORY
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sub_category_list_create(request):
    if request.method == 'GET':
        categories = SubCategory.objects.all()
        serializer = SubCategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Sub category created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def sub_category_detail(request, id):
    category = get_object_or_404(SubCategory, id=id)
    serializer = SubCategorySerializer(category)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def sub_category_update(request, id):
    category = get_object_or_404(SubCategory, id=id)
    serializer = SubCategorySerializer(category, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Sub category updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def sub_category_delete(request, id):
    category = get_object_or_404(SubCategory, id=id)
    category.delete()
    return Response({"message": "Sub category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# PRODUCT IMAGES
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_image_list_create(request):
    if request.method == 'GET':
        images = ProductImage.objects.all()
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = ProductImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product image added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_image_detail(request, id):
    image = get_object_or_404(ProductImage, id=id)
    serializer = ProductImageSerializer(image)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_image_delete(request, id):
    image = get_object_or_404(ProductImage, id=id)
    image.delete()
    return Response({"message": "Product image deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# OFFERS
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def offer_list_create(request):
    if request.method == 'GET':
        offers = Offer.objects.all()
        serializer = OfferSerializer(offers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = OfferSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Offer created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 

@api_view(['GET'])
def offer_detail(request, id):
    offer = get_object_or_404(Offer, id=id)
    serializer = OfferSerializer(offer)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def offer_update(request, id):
    offer = get_object_or_404(Offer, id=id)
    serializer = OfferSerializer(offer, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Offer updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def offer_delete(request, id):
    offer = get_object_or_404(Offer, id=id)
    offer.delete()
    return Response({"message": "Offer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# PRODUCT REVIEWS
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_review_list_create(request):
    if request.method == 'GET':
        reviews = ProductReview.objects.all()
        serializer = ProductReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = ProductReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Product review added successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    return Response({"message": "Validation failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_review_detail(request, id):
    review = get_object_or_404(ProductReview, id=id)
    serializer = ProductReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_review_delete(request, id):
    review = get_object_or_404(ProductReview, id=id)
    review.delete()
    return Response({"message": "Review deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
