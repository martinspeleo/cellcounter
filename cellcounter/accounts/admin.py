from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from cellcounter.accounts.models import UserProfile, PasswordResetKey

admin.site.unregister(User)

class UserProfileInline(admin.StackedInline):
    model = UserProfile

class UserProfileAdmin(UserAdmin):
    inlines = [ UserProfileInline, ]

class PasswordResetKeyAdmin(admin.ModelAdmin):
    pass 

admin.site.register(User, UserProfileAdmin)
admin.site.register(PasswordResetKey, PasswordResetKeyAdmin)


