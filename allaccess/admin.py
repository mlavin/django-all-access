from django.contrib import admin

from .models import Provider, AccountAccess


class ProviderAdmin(admin.ModelAdmin):
    "Admin customization for OAuth providers."

    list_display = ('name', 'enabled', )


class AccountAccessAdmin(admin.ModelAdmin):
    "Admin customization for accounts."

    list_display = ('__str__', 'provider', 'user', 'created', 'modified', )
    list_filter = ('provider', 'created', 'modified', )


admin.site.register(Provider, ProviderAdmin)
admin.site.register(AccountAccess, AccountAccessAdmin)
