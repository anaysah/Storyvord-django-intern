# write basic code
from django.urls import path
from tasks.views import protected_view
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet
from django.urls import include

router = DefaultRouter()
router.register(r'', TaskViewSet)

urlpatterns = [
    path('protected/', protected_view),  # Protected API
    # for testing protected API
    path('', include(router.urls)),
]