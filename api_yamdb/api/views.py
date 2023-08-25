import uuid

from django.core.mail import send_mail
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets, status, serializers
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Review, Titles, Categories, Genres
from api.serializers import (TitlesSerializer,
                             CategoriesSerializer,
                             GenresSerializer,
                             SignUpSerializer,
                             UserSerializer,
                             CommentSerializer,
                             ReviewSerializer,
                             TokenSerializer,
                             )
from api.permissions import (IsAdminOrAuthor,
                             IsAdminOrAuthorOrModerator,
                             )
from users.models import User


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
            email=email
        )
    except IntegrityError:
        return Response(
            'Пользователь с такими полями уже зарегистрирован',
            status=status.HTTP_400_BAD_REQUEST
        )
    confirmation_code = str(uuid.uuid4())
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        'Код подверждения', confirmation_code,
        ['admin@email.com'], (email, ), fail_silently=False
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
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrAuthor, )


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Titles.objects.all()
    serializer_class = TitlesSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('category', 'genre', 'name', 'year')


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenresViewSet(viewsets.ModelViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenresSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrAuthorOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        reviews_id = self.kwargs.get('pk')
        title = get_object_or_404(Titles, id=title_id)

        if not reviews_id:
            return title.reviews.all()
        return title.reviews.filter(id=reviews_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(
            author=self.request.user,
            title=Titles.objects.get(id=title_id),
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrAuthorOrModerator,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        reviews_id = self.kwargs.get('review_id')
        comment_id = self.kwargs.get('pk')
        title = get_object_or_404(Titles, id=title_id)
        review = get_object_or_404(Review, id=reviews_id)

        if not comment_id:
            return review.comments.all()
        return review.comments.filter(id=comment_id)

    def perform_create(self, serializer):
        reviews_id = self.kwargs.get('review_id')
        serializer.save(
            author=self.request.user,
            title=Titles.objects.get(id=reviews_id),
        )
