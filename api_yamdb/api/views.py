import uuid

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from api.filter import GenreFilter
from api.permissions import (AdminOrReadOnly, IsAdminOrAuthor,
                             IsAdminOrAuthorOrModerator)
from api.serializers import (CategoriesSerializer, CommentSerializer,
                             GenresSerializer, NoRoleSerializer,
                             ReviewSerializer, SignUpSerializer,
                             TitlesPostSerializer, TitlesSerializer,
                             TokenSerializer, UserSerializer)
from reviews.models import Category, Genres, Review, Title
from users.models import User


class CreateListDestroy(mixins.CreateModelMixin,
                        mixins.ListModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data['email']
    username = serializer.validated_data['username']
    try:
        user, create = User.objects.get_or_create(
            username=username,
            email=email,
        )
    except IntegrityError:
        return Response(
            {'detail': 'Отсутствует обязательное поле или оно некорректно'},
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подверждения', confirmation_code,
        [settings.EMAIL_SEND_MAILBOX], (email, ), fail_silently=False
    )
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    confirmation_code = serializer.validated_data['confirmation_code']
    userdata = get_object_or_404(User, username=username)
    if confirmation_code == userdata.confirmation_code:
        token = str(AccessToken.for_user(userdata))
        return Response({'token': token}, status=status.HTTP_201_CREATED)
    return Response(
        {'detail': 'Отсутствует обязательное поле или оно некорректно'},
        status=status.HTTP_400_BAD_REQUEST
    )


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrAuthor, )
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'],
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated, )
    )
    def me_patch(self, request):
        user = get_object_or_404(User, username=self.request.user)
        if request.data.get('username') == 'me':
            return Response(
                {'detail': "Использовать имя 'me' в качестве `username`"
                 "запрещено."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'GET':
            serializer = NoRoleSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = NoRoleSerializer(user,
                                          data=request.data,
                                          partial=True,
                                          )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


class TitlesViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'patch']
    queryset = Title.objects.all()
    serializer_class = TitlesSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = GenreFilter
    search_fields = ('category__slug', 'genre__slug', 'name', 'year',)
    permission_classes = [AdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitlesSerializer
        return TitlesPostSerializer


class CategoriesViewSet(CreateListDestroy):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminOrReadOnly]


class GenresViewSet(CreateListDestroy):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [AdminOrReadOnly]


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""
    http_method_names = ['get', 'post', 'delete', 'patch']
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrModerator,)
    pagination_class = LimitOffsetPagination
    lookup_url_kwarg = 'review_id'

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        reviews_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, id=title_id)

        if not reviews_id:
            return title.reviews.all()
        return title.reviews.filter(id=reviews_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(Title, id=title_id),
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    http_method_names = ['get', 'post', 'delete', 'patch']
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrAuthorOrModerator,)
    pagination_class = LimitOffsetPagination
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        reviews_id = self.kwargs.get('review_id')
        comment_id = self.kwargs.get('comment_id')
        review = get_object_or_404(Review, id=reviews_id)

        if not comment_id:
            return review.comments.all()
        return review.comments.filter(id=comment_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        reviews_id = self.kwargs.get('review_id')
        get_object_or_404(Title, id=title_id)

        serializer.save(
            author=self.request.user,
            review=get_object_or_404(Review, id=reviews_id),
        )
