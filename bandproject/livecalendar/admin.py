from django.contrib import admin
from .models import Band,Live,Place,CustomUser
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


# Register your models here.
class LiveAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'place')
    list_filter = ['date']

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    list_filter = ['name']


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('userimage','username','screenname','email', 'password')}),
        (_('Favorite band'), {'fields': ['favorite_band']}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('username', 'screenname', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'username', 'screnname')
    filter_horizontal = ('groups', 'user_permissions','favorite_band')


admin.site.register(Live,LiveAdmin)
admin.site.register(Band)
admin.site.register(Place,PlaceAdmin)
admin.site.register(CustomUser,MyUserAdmin)
