from django.contrib import admin
from .models import Category, Event, EventRSVP

class EventRSVPInline(admin.TabularInline):
    model = EventRSVP
    extra = 1
    readonly_fields = ('timestamp',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'location', 'category')
    list_filter = ('category', 'date')
    search_fields = ('name', 'location')
    inlines = [EventRSVPInline]  # Manage participants via RSVPs

@admin.register(EventRSVP)
class EventRSVPAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'get_status', 'timestamp')
    list_filter = ('status', 'event__category')
    search_fields = ('user__username', 'event__name')
    readonly_fields = ('timestamp',)

    def get_status(self, obj):
        return obj.get_status_display()
    get_status.short_description = 'Status'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description_short')
    search_fields = ('name',)

    def description_short(self, obj):
        return obj.description[:50] + '...' if obj.description else ''
    description_short.short_description = 'Description'