from django.contrib import admin
from .models import *

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('date_joined',)  # Orders by date joined

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'age')
    list_select_related = ('user',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    ordering = ('user__last_name',)  # Orders by patient's last name
    readonly_fields = ('user',)  # Make 'user' field read-only

    class IssueInline(admin.TabularInline):
        model = Issue
        extra = 0  # No extra empty fields when adding issues

    inlines = [IssueInline]

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialty', 'license_number', 'years_experience')
    list_filter = ('specialty',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'license_number')
    ordering = ('user__last_name',)  # Orders by doctor's last name
    readonly_fields = ('user',)  # Make 'user' field read-only

    # Inline model for Issues related to the doctor
    class IssueInline(admin.TabularInline):
        model = Issue
        extra = 0  # No extra empty fields when adding issues

    inlines = [IssueInline]

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'doctor', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'patient__user__username', 'doctor__user__username')
    ordering = ('-created_at',)  # Orders by the latest created issue

    # Optionally, add bulk actions
    actions = ['mark_as_resolved']

    def mark_as_resolved(self, request, queryset):
        queryset.update(status='Resolved')
    mark_as_resolved.short_description = "Mark selected issues as resolved"

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'uploaded_at', 'file')
    list_filter = ('uploaded_at',)
    search_fields = ('issue__title', 'file')
    ordering = ('-uploaded_at',)  # Orders by the latest uploaded document

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'author', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('issue__title', 'author__username')
    ordering = ('-created_at',)  # Orders by the latest created comment

admin.site.register(PatientRequest)