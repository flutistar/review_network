from django.contrib import admin
from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer_company_name'] 
    model = Order
    # fieldsets = (
    #     (None, {
    #         'fields': ('order_id','buyer_company_name')
    #     }),
    # )
    readonly_fields = ('id', )
    class Media:
        js = (
            'js/admin.js',   # inside app static folder
        )

admin.site.register(Order, OrderAdmin)