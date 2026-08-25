import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import ChangePasswordSerializer, RegisterSerializer, UserSerializer

User = get_user_model()


def tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class RegisterView(generics.CreateAPIView):
    """Inscription classique (2.2.1)."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'user': UserSerializer(user).data, **tokens_for_user(user)},
            status=status.HTTP_201_CREATED,
        )


class MeView(generics.RetrieveUpdateAPIView):
    """Profil courant + préférences culinaires (2.2.5)."""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'detail': 'Mot de passe actuel incorrect.'}, status=400)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'detail': 'Mot de passe mis à jour.'})


class OAuthLoginView(APIView):
    """
    Connexion / inscription via OAuth2 (Google, GitHub, Microsoft) - 2.2.1 / 2.2.5.

    Le frontend effectue le "authorization code flow" avec le fournisseur puis
    poste ici { "code": "...", "redirect_uri": "..." }. Ce endpoint échange le
    code contre un access_token, récupère les infos utilisateur, puis crée ou
    retrouve le compte SUPMEAL correspondant et retourne des tokens JWT SUPMEAL.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, provider):
        config = settings.OAUTH_PROVIDERS.get(provider)
        if not config or not config['client_id']:
            return Response(
                {'detail': f"Fournisseur OAuth2 '{provider}' non configuré."},
                status=400,
            )

        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')
        if not code or not redirect_uri:
            return Response({'detail': 'code et redirect_uri requis.'}, status=400)

        token_resp = requests.post(
            config['token_url'],
            data={
                'client_id': config['client_id'],
                'client_secret': config['client_secret'],
                'code': code,
                'redirect_uri': redirect_uri,
                'grant_type': 'authorization_code',
            },
            headers={'Accept': 'application/json'},
            timeout=10,
        )
        if token_resp.status_code != 200:
            return Response({'detail': 'Échec échange token OAuth2.'}, status=400)
        access_token = token_resp.json().get('access_token')
        if not access_token:
            return Response({'detail': 'Token OAuth2 manquant.'}, status=400)

        userinfo_resp = requests.get(
            config['userinfo_url'],
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )
        if userinfo_resp.status_code != 200:
            return Response({'detail': 'Échec récupération profil OAuth2.'}, status=400)
        info = userinfo_resp.json()

        oauth_id = str(info.get('sub') or info.get('id'))
        email = info.get('email') or f"{provider}_{oauth_id}@supmeal.local"
        username = info.get('login') or info.get('name') or f"{provider}_{oauth_id}"

        user, created = User.objects.get_or_create(
            oauth_provider=provider,
            oauth_id=oauth_id,
            defaults={'email': email, 'username': username},
        )
        if created:
            user.set_unusable_password()
            user.save()

        return Response({'user': UserSerializer(user).data, **tokens_for_user(user)})
