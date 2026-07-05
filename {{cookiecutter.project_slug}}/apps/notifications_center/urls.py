from django.urls import path

from . import views

app_name = "notifications_center"

urlpatterns = [
    path("", views.notification_list, name="list"),
    path("<int:notification_id>/read/", views.mark_read, name="mark_read"),
    path("<int:notification_id>/unread/", views.mark_unread, name="mark_unread"),
    path("read-all/", views.mark_all_read, name="mark_all_read"),
]
