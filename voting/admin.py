from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from .models import Choice, Question
from .models import Pemilih
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

#from .forms import CustomUserCreationForm, CustomUserChangeForm
#from .models import CustomUser

#from django.contrib.auth.models import Permission
admin.site.unregister(User)

#Unregister the provided model admin

#Register out own model admin, based on the default UserAdmin
class PemilihInLine(admin.StackedInline):
    model = Pemilih
    fk_name = 'user'

@admin.register(User)
class CustomUserAdmin(UserAdmin):

    inlines = (PemilihInLine, )
    #prevent date joined get edited
    readonly_fields = [
        'date_joined',
        'last_login',
    ]

    actions = ('active_users', 'delete_users')
    def active_users(self, request, queryset):
        cnt = queryset.filter(is_active=False).update(is_active=True)
        self.message_user(request, 'Activated {} users.'.format(cnt))
    active_users.short_description = 'Aktifkan Pengguna'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.has_perm('auth.change_user'):
            del actions['activate_users']
        return actions
    pass


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        is_staff = request.user.is_staff
        disabled_fields = set()

        if not is_superuser:
        #making username field cant edit
        #preven other than superuser can edit superuser status
            disabled_fields |= {
                'first_name',
                'email',
                'last_name',
                'is_staff',
                'is_active',
                'is_superuser',
                'user_permissions',
                'groups',
                'password_change',
                'password_reset',
                'change_user',
            }

            #prevent non-superusers from editing their own permissions
        if(
            not is_superuser
            and obj is not None
            and obj == request.user
            ):
            disabled_fields |= {
                'is_staff',
                'first_name',
                'email',
                'last_name',
                'is_superuser',
                'groups',
                'user_permissions',
                }
        if is_superuser:
            disabled_fields |= {
                'group',
            }

        for f in disabled_fields:
            if f in form.base_fields:
                form.base_fields[f].disabled = True

        return form

    def get_queryset(self, request):
        qs = super(UserAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_superuser = False, is_staff = False)
        return qs

class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 1

    readonly_fields = ('votes','enkripsi_stats')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['choice_text','choice_text2','votes','image','enkripsi_stats']
        else:
            return ['votes','enkripsi_stats']


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':['question_text']}),
        ('Date Information Start', {'fields': ['pub_date','pub_date_end'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInLine]
    list_display = ('question_text','pub_date','pub_date_end','was_published_recently', 'status')
    list_filter = ['pub_date']
    search_fields = ['question_text']
    actions = ('make_published','make_drafted')

    def make_published(self, request, queryset):
        rows_updated = queryset.update(status='p')
        if rows_updated == 1:
            message_bit = "1 pemungutan"
        else :
            message_bit = "%s pemungutan telah"%rows_updated
            self.message_user(request, "%s berhasil dibuat publik" % message_bit)


    def make_drafted(self, request, queryset):
        rows_updated = queryset.update(status='d')
        if rows_updated == 1:
            message_bit = "1 pemungutan"
        else :
            message_bit = "%s pemungutan telah"%rows_updated
            self.message_user(request, "%s behasil di arsipkan" % message_bit)


    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['question_text']
        else:
            return []

admin.site.register(Question, QuestionAdmin)
admin.site.unregister(Group)