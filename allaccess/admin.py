from django.contrib import admin

from .models import Provider, AccountAccess


class ProviderAdmin(admin.ModelAdmin):
    "Admin customization for OAuth providers."


class AccountAccessAdmin(admin.ModelAdmin):
    "Admin customization for accounts."


admin.site.register(Provider, ProviderAdmin)
admin.site.register(AccountAccess, AccountAccessAdmin)
