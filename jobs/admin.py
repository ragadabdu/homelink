from django.contrib import admin

from .models import Freelancer, Business

admin.site.register(Freelancer)
admin.site.register(Business)

from django.contrib import admin
from .models import WorkerCategory

@admin.register(WorkerCategory)
class WorkerCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'demand_count')
    search_fields = ('name',)
    list_filter = ('name',)
    
from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'transaction_id', 'status', 'created_at')
    search_fields = ('user__username', 'transaction_id', 'status')
    list_filter = ('status', 'created_at')
