from django.contrib import admin
from .models import *


class StateInline(admin.TabularInline):
    model = State
    extra = 0


class CountryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']
    search_fields = ['name', 'code']
    inlines = [
        StateInline
    ]


class StateAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'country']
    search_fields = ['name', 'country__name']
    list_filter = ['country']


class CityAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code']
    search_fields = ['name', 'state__name']


admin.site.register(Country, CountryAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(City, CityAdmin)

