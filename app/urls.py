from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home),
    path('login/', views.login),
    path('register/', views.register),
    #path('/personal', views.personal),
    path('deviceslist/', views.deviceslist),
    path('adddevice/', views.adddevice),
    path('devaccountrule/', views.devaccountrule),
    #path('/devicesmap', views.devicesmap),
    path('realtimemonitor/', views.realtimemonitor),
    path('dynamicdata/', views.dynamicdata),
    path('energystatistics/', views.energystatistics),
    #path('/deviceinfo', views.deviceinfo),
    path('dashboard/', views.dashboard),
    path('warningmessage/', views.warningmessage),
    path('remotecontrol/', views.remotecontrol),
    path('parameterset/', views.parameterset),
    #path('/ontimeswitch', views.ontimeswitch),
    #path('/addswitch', views.addswitch),
    #path('/oplog', views.oplog),
]
