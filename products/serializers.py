from rest_framework import serializers

from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "parent"]
        
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    avg_rating = serializers.FloatField(read_only=True,default=None)
    review_count = serializers.IntegerField(read_only=True,default=0)
    
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "category",
            "image",
            "stock",
            "avg_rating",
            "review_count",
        ]