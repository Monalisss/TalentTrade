from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from Talent.views import(
HomePageView,
UserAccountView, 
FormDeleteView, 
FormUpdateView,
CustomLoginView,
CustomRegisterView,
ProfileEdit,
logout_view,
ChatView,
InboxView,
)
from Talent.views import AddTalentView
from Talent.views import InboxView



urlpatterns = [
    path('admin/', admin.site.urls),

    path("accounts/login/", CustomLoginView.as_view(), name="login"),

    path ("logout/", logout_view, name='logout'),

    path ("signup", CustomRegisterView.as_view(), name= "register"),

    path("", HomePageView.as_view(), name="home"),

    path("add_talent/", AddTalentView.as_view(), name="add_talent"),

#USER ACCOUNT 

    path("user/account", UserAccountView.as_view(), name="user_account"),

#USER EDIT INFO 

    path("profile/edit/", ProfileEdit.as_view(), name="edit_profile"),

# UPDATE POSTS AND DELETE

    path("user/<int:pk>/Update", FormUpdateView.as_view(), name="update"),


    path("user/<int:pk>/delete", FormDeleteView.as_view(), name="delete"),

    path('chat/<int:user_id>/', ChatView.as_view(), name='chat'),

    path('inbox/', InboxView.as_view(), name="inbox"),
]

# Media files (photos) 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)