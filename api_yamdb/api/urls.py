from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (TitlesViewSet,
                       GenresViewSet,
                       CategoriesViewSet,
                       UserViewSet,
                       signup,
                       )

router = DefaultRouter()
router.register('users', UserViewSet)
router.register(r'/titles', TitlesViewSet)
router.register(r'/genres', GenresViewSet)
router.register(r'/categories', CategoriesViewSet)

urlpatterns = [
    path('v1', include(router.urls)),
    path('v1/auth/signup/', signup)
]
