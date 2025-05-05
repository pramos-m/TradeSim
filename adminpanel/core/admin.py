from django.contrib import admin
from .models import User, Stock, Transaction, Sector

admin.site.register(User)
admin.site.register(Stock)
admin.site.register(Transaction)
admin.site.register(Sector)