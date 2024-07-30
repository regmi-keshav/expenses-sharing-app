# expenses_app/admin.py

from django.contrib import admin
from .models import User, Expense, ExpenseSplit

from django.contrib import admin
from .models import User, Expense, ExpenseSplit


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'mobile_number', 'is_active')
    search_fields = ('email', 'name', 'mobile_number')


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('payer', 'total_amount',
                    'description', 'date', 'split_method')
    search_fields = ('payer__email', 'description')


@admin.register(ExpenseSplit)
class ExpenseSplitAdmin(admin.ModelAdmin):
    list_display = ('expense', 'user', 'amount', 'percentage')
