
from django.contrib import admin
from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls), 
    path('',views.login_user, name="login_user"),
    path('registration',views.register_user,name="registration"),
    path('upload_resume/',views.upload_resume, name="upload_resume"),
    path('resume_list/',views.resume_list,name="resume_list"),
    path('about/',views.about_us,name="about")
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)