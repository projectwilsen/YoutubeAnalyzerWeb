from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name ="index"),
    path('findcomment',views.findcomment, name = "findcomment")
]