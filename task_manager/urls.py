from django.urls import path
from django.http import HttpResponse
from tasks.views import protected_view
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # Gets access & refresh tokens
    TokenRefreshView,      # Gets a new access token using refresh token
)
from django.urls import include
from tasks.views import register




urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # //test url which returns a simple response in json
    path('api/test/', lambda request: HttpResponse('{"message": "Hello, World!"}', content_type='application/json')),

    path('api/register/', register, name='register'), 
    # register but i have not created new app named users instead i will use the default User model and have created a new serializer in tasks app
    # we dont have much implementation for users so we will do that in tasks app itself

    # add all urls.py from tasks app
    path('api/tasks/', include('tasks.urls')),
    
]