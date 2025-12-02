from django.contrib import admin
from .models import *
# Register your models here.

class RacerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

class ConstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

class SeasonAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')

class SeasonRacerAdmin(admin.ModelAdmin):
    list_display = ('racer', 'season')

class SeasonConstructorAdmin(admin.ModelAdmin):
    list_display = ('constructor', 'season')

class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'season')

class QualifyingResultAdmin(admin.ModelAdmin):
    list_display = ('racer', 'race')

class RaceResultAdmin(admin.ModelAdmin):
    list_display = ('racer', 'race')


admin.site.register(Racer, RacerAdmin)
admin.site.register(Constructor, ConstructorAdmin)
admin.site.register(Season, SeasonAdmin)
admin.site.register(SeasonRacer, SeasonRacerAdmin)
admin.site.register(SeasonConstructor, SeasonConstructorAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(QualifyingResult, QualifyingResultAdmin)
admin.site.register(RaceResult, RaceResultAdmin)