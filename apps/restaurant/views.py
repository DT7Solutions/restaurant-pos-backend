from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max
from .models import *
from .serializers import *

# ============================================================
# HELPER FUNCTION — assign display order automatically
# ============================================================
def assign_display_order(model, data, parent_field=None):
    if not data.get("display_order"):
        qs = model.objects.all()
        if parent_field and data.get(parent_field):
            qs = qs.filter(**{parent_field: data[parent_field]})
        data["display_order"] = (qs.aggregate(Max("display_order"))["display_order__max"] or 0) + 1
    return data

# ============================================================
# PRODUCT CHOICES
# ============================================================
@api_view(['GET'])
def get_product_choices(request):
    try:
        return Response({
            "variant_choices": [{"value": v[0], "label": v[1]} for v in ProductItem._meta.get_field('variant_type').choices],
            "unit_choices": [{"value": v[0], "label": v[1]} for v in ProductItem._meta.get_field('quantity_unit').choices],
            "currency_choices": [{"value": v[0], "label": v[1]} for v in ProductItem._meta.get_field('currency_symbol').choices],
        })
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ============================================================
# MAIN CATEGORY
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def main_category_list_create(request):
    if request.method == 'GET':
        return Response(MainCategorySerializer(MainCategory.objects.all(), many=True).data)

    data = assign_display_order(MainCategory, request.data)
    s = MainCategorySerializer(data=data)
    if s.is_valid():
        s.save()
        return Response({"message": "Main category added", "data": s.data}, status=status.HTTP_201_CREATED)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def main_category_detail(request, id):
    obj = get_object_or_404(MainCategory, id=id)
    return Response(MainCategorySerializer(obj).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def main_category_update(request, id):
    obj = get_object_or_404(MainCategory, id=id)
    data = assign_display_order(MainCategory, request.data)
    s = MainCategorySerializer(obj, data=data, partial=True)
    if s.is_valid():
        s.save()
        return Response({"message": "Main category updated", "data": s.data}, status=status.HTTP_200_OK)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def main_category_delete(request, id):
    obj = get_object_or_404(MainCategory, id=id)
    obj.delete()
    return Response({"message": "Main category deleted"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# SUB CATEGORY
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def sub_category_list_create(request):
    if request.method == 'GET':
        return Response(SubCategorySerializer(SubCategory.objects.all(), many=True).data)

    data = assign_display_order(SubCategory, request.data, 'main_category')
    s = SubCategorySerializer(data=data)
    if s.is_valid():
        s.save()
        return Response({"message": "Sub category added", "data": s.data}, status=status.HTTP_201_CREATED)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def sub_category_detail(request, id):
    obj = get_object_or_404(SubCategory, id=id)
    return Response(SubCategorySerializer(obj).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def sub_category_update(request, id):
    obj = get_object_or_404(SubCategory, id=id)
    data = assign_display_order(SubCategory, request.data, 'main_category')
    s = SubCategorySerializer(obj, data=data, partial=True)
    if s.is_valid():
        s.save()
        return Response({"message": "Sub category updated", "data": s.data}, status=status.HTTP_200_OK)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def sub_category_delete(request, id):
    obj = get_object_or_404(SubCategory, id=id)
    obj.delete()
    return Response({"message": "Sub category deleted"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# PRODUCT ITEMS
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_items_list_create(request):
    if request.method == 'GET':
        qs = ProductItem.objects.select_related('main_category', 'sub_category').prefetch_related('offers')
        return Response(ProductItemSerializer(qs, many=True, context={'request': request}).data)

    data = assign_display_order(ProductItem, request.data, 'sub_category')
    s = ProductItemSerializer(data=data, context={'request': request})
    if s.is_valid():
        s.save(created_by=request.user)
        return Response({"message": "Product created", "data": s.data}, status=status.HTTP_201_CREATED)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_item_detail(request, id):
    obj = get_object_or_404(ProductItem, id=id)
    return Response(ProductItemSerializer(obj, context={'request': request}).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def product_item_update(request, id):
    obj = get_object_or_404(ProductItem, id=id)
    data = assign_display_order(ProductItem, request.data, 'sub_category')
    s = ProductItemSerializer(obj, data=data, partial=True, context={'request': request})
    if s.is_valid():
        s.save()
        return Response({"message": "Product updated", "data": s.data}, status=status.HTTP_200_OK)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_item_delete(request, id):
    obj = get_object_or_404(ProductItem, id=id)
    obj.delete()
    return Response({"message": "Product deleted"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# OFFERS
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def offer_list_create(request):
    if request.method == 'GET':
        return Response(OfferSerializer(Offer.objects.all(), many=True).data)

    s = OfferSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response({"message": "Offer created", "data": s.data}, status=status.HTTP_201_CREATED)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def offer_detail(request, id):
    obj = get_object_or_404(Offer, id=id)
    return Response(OfferSerializer(obj).data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def offer_update(request, id):
    obj = get_object_or_404(Offer, id=id)
    s = OfferSerializer(obj, data=request.data, partial=True)
    if s.is_valid():
        s.save()
        return Response({"message": "Offer updated", "data": s.data}, status=status.HTTP_200_OK)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def offer_delete(request, id):
    obj = get_object_or_404(Offer, id=id)
    obj.delete()
    return Response({"message": "Offer deleted"}, status=status.HTTP_204_NO_CONTENT)

# ============================================================
# PRODUCT REVIEWS
# ============================================================
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def product_review_list_create(request):
    if request.method == 'GET':
        return Response(ProductReviewSerializer(ProductReview.objects.all(), many=True).data)

    s = ProductReviewSerializer(data=request.data)
    if s.is_valid():
        s.save()
        return Response({"message": "Product review added", "data": s.data}, status=status.HTTP_201_CREATED)
    return Response({"errors": s.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def product_review_detail(request, id):
    obj = get_object_or_404(ProductReview, id=id)
    return Response(ProductReviewSerializer(obj).data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def product_review_delete(request, id):
    obj = get_object_or_404(ProductReview, id=id)
    obj.delete()
    return Response({"message": "Review deleted"}, status=status.HTTP_204_NO_CONTENT)
