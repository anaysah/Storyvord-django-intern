# write basic code
from django.urls import path
from tasks.views import protected_view

urlpatterns = [
    path('protected/', protected_view),  # Protected API
    # for testing protected API's
]