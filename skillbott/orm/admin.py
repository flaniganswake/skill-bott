from .models import Category, Customer, Inventory, Topic
from django.contrib import admin


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'tagline', 'description', 'instructions',)
    exclude = ('type', 'yellow_choices', 'green_choices', 'categories')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('hover',)
    exclude = ('type', 'topics', 'inventory',)


class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'hover', 'name2', 'hover2')
    exclude = ('yellow', 'green', 'answers', 'category',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'access_code', 'url', 'email', 'profile',)
    exclude = ('users',)


admin.site.register(Inventory, InventoryAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Customer, CustomerAdmin)
