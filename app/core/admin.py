from django.contrib import admin

from .models import User, Bank, Account, Transfer


admin.site.register(User)
admin.site.register(Bank)
admin.site.register(Account)
admin.site.register(Transfer)
