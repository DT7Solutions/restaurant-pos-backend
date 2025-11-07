from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.authentication.models import *

# ============================================================
# CATEGORY MODELS
# ============================================================
class MainCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Auto assign display order
        if not self.display_order:
            max_order = MainCategory.objects.aggregate(models.Max("display_order"))["display_order__max"] or 0
            self.display_order = max_order + 1
        super().save(*args, **kwargs)
        # Ensure continuous order
        for i, o in enumerate(MainCategory.objects.order_by("display_order", "id"), 1):
            if o.display_order != i:
                MainCategory.objects.filter(id=o.id).update(display_order=i)
        # Cascade status
        self.subcategories.update(is_active=self.is_active)
        ProductItem.objects.filter(main_category=self).update(is_active=self.is_active)

    class Meta:
        ordering = ["display_order", "id"]

    def __str__(self): return self.name

class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="subcategories")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.display_order:
            qs = SubCategory.objects.filter(main_category=self.main_category)
            max_order = qs.aggregate(models.Max("display_order"))["display_order__max"] or 0
            self.display_order = max_order + 1
        super().save(*args, **kwargs)
        for i, o in enumerate(SubCategory.objects.filter(main_category=self.main_category).order_by("display_order", "id"), 1):
            if o.display_order != i: SubCategory.objects.filter(id=o.id).update(display_order=i)
        self.products.update(is_active=self.is_active)

    class Meta:
        unique_together = ("main_category", "name")
        ordering = ["display_order", "id"]

    def __str__(self): return f"{self.main_category.name} → {self.name}"

# ============================================================
# OFFERS MODEL
# ============================================================
class Offer(models.Model):
    OFFER_TYPE_CHOICES = [('flat', 'Flat Discount'), ('percent', 'Percentage Discount')]
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES, default='flat')
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    def __str__(self): return f"{self.name} ({self.discount_value}{'%' if self.offer_type == 'percent' else ''})"

# ============================================================
# PRODUCT ITEM MODEL
# ============================================================
VARIANT_CHOICES = [('Veg','VEG'),('Non-Veg','NON-VEG'),('Eggetarian','EGGETARIAN'),('Vegan','VEGAN'),('None','NONE')]
UNIT_CHOICES = [('item','Item'),('pcs','Pieces'),('plate','Plate'),('bowl','Bowl'),('cup','Cup'),
                ('glass','Glass'),('ml','ml'),('l','Litre'),('g','Gram'),('kg','Kg'),('None','None')]
CURRENCY_CHOICES = [('$','US Dollar ($)'),('₹','Indian Rupee (₹)'),('€','Euro (€)'),('£','British Pound (£)')]

class ProductItem(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name="products")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    prepare_time = models.PositiveIntegerField(default=10, help_text="Time in minutes")
    variant_type = models.CharField(max_length=20, choices=VARIANT_CHOICES, default='None')
    quantity_value = models.FloatField(default=1.0, validators=[MinValueValidator(0.0)])
    quantity_unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='None')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency_symbol = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='$')
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    stock_available = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    max_order_quantity = models.PositiveIntegerField(default=10)
    offers = models.ManyToManyField(Offer, blank=True, related_name="products")
    customizations = models.TextField(blank=True, null=True, help_text="Custom options or instructions")
    rating_avg = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    display_order = models.PositiveIntegerField(blank=True, null=True)
    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_products")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='menu_items/', blank=True, null=True)
    image_alt = models.CharField(max_length=150, blank=True, null=True, help_text="Alternative text for accessibility/SEO")

    class Meta:
        ordering = ['display_order', 'id']

    def save(self, *args, **kwargs):
        if not self.main_category.is_active or (self.sub_category and not self.sub_category.is_active):
            self.is_active = False
        base, slug, n = slugify(self.name), slugify(self.name), 1
        while ProductItem.objects.filter(slug=slug).exclude(id=self.id).exists():
            slug, n = f"{base}-{n}", n + 1
        self.slug = slug
        if not self.image_alt: self.image_alt = self.name
        if self.image:
            ext = self.image.name.split('.')[-1].lower()
            clean_name = f"{self.slug}.{ext}"
            if not self.image.name.startswith("menu_items/"):
                self.image.name = f"menu_items/{clean_name}"
            else:
                parts = self.image.name.split('/')
                if len(parts) > 2 and parts[0] == "menu_items" and parts[1] == "menu_items":
                    self.image.name = f"menu_items/{clean_name}"
                elif parts[0] == "menu_items" and len(parts) == 2:
                    self.image.name = f"menu_items/{clean_name}"
        if not self.display_order:
            qs = ProductItem.objects.filter(main_category=self.main_category)
            if self.sub_category: qs = qs.filter(sub_category=self.sub_category)
            max_order = qs.aggregate(models.Max("display_order"))["display_order__max"] or 0
            self.display_order = max_order + 1
        super().save(*args, **kwargs)
        q = ProductItem.objects.filter(main_category=self.main_category)
        if self.sub_category: q = q.filter(sub_category=self.sub_category)
        for i, o in enumerate(q.order_by("display_order", "id"), 1):
            if o.display_order != i: ProductItem.objects.filter(id=o.id).update(display_order=i)

    class Meta:
        ordering = ['display_order', 'id']
    def __str__(self): return f"{self.name} ({self.currency_symbol}{self.price})"
    @property
    def image_url(self): return self.image.url if self.image else None

# ============================================================
# PRODUCT REVIEW MODEL
# ============================================================
class ProductReview(models.Model):
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self): return f"{self.product.name} - {self.rating}★"
