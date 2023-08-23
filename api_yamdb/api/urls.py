from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TitlesViewSet, GenresViewSet, CategoriesViewSet

router = DefaultRouter()
router.register(r'/titles', TitlesViewSet)
router.register(r'/genres', GenresViewSet)
router.register(r'/categories', CategoriesViewSet)

urlpatterns = [
    path('v1', include(router.urls)),
]
