from django.contrib import admin

from apps.trips.models import Trip, TripParticipant


class TripAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "trip",
        "user",
        "shares",
    ]


admin.site.register(Trip)
admin.site.register(TripParticipant)
