from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = [
        'username', 'email', 'name', 'surname', 'given_name', 
        'preferred_username', 'nickname', 'phone', 'location', 
        'email_verified', 'is_staff', 'is_active'
    ]

    list_filter = ['is_staff', 'is_active', 'email_verified']

    search_fields = ['username', 'email', 'name', 'surname', 'given_name', 'preferred_username', 'nickname']

    ordering = ['username']

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'name', 'surname', 'given_name', 'preferred_username', 
                'nickname', 'phone', 'location', 'email_verified', 'sub', 'nonce'
            ),
        }),
    )


    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': (
                'name', 'surname', 'given_name', 'preferred_username', 
                'nickname', 'phone', 'location', 'email_verified', 'sub', 'nonce'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


class UserInline(admin.TabularInline):  # admin.StackedInline для другого стиля отображения
    model = User.groups.through  
    extra = 0  
    verbose_name = 'Пользователь'
    verbose_name_plural = 'Пользователи'




class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_users')
    inlines = [UserInline]  
    def display_users(self, obj):
        return ", ".join([user.username for user in obj.user_set.all()])

    display_users.short_description = 'Пользователи'  


admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
