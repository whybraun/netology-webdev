from django.contrib import admin
from .models import Product, Stock, StockProduct

admin.site.register(Product)
admin.site.register(Stock)
admin.site.register(StockProduct)
