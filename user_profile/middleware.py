''' Middleware class to authenticate the incoming requests
for jwt tokens unless the requests are to login or signup page.
'''
import jwt
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed, ParseError


class TokenRetrievalMixin:
     ''' Mixin containing the logic to retrieve the token out
     of authorization header.
     '''
     def retrieve_access_token(self, request):
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            raise Exception("Authorization header is missing!")
        
        auth_parts = authorization_header.split()
        if  len(auth_parts) != 2 or auth_parts[0].lower() != 'bearer':
            raise Exception("Authorization header is not in proper format!")
        
        return auth_parts[1]
     

class UserValidationMixin:
    ''' Validates if the given user is present and populates request
    object with user object.'''

    def validate_user(self, payload, request):
        user_id = payload.get('user_id')
        if user_id is None:
            raise Exception('User id is not present in token!')

        User = get_user_model()
        try:
            user = User.objects.filter(pk=user_id).first()
            # Add the user to the request object for later use
            request.user = user
        except User.DoesNotExist:
            raise Exception("Invalid user.")


class JWTAuthenticationMiddleware(
      MiddlewareMixin,
      TokenRetrievalMixin,
      UserValidationMixin
    ):
    ''' Get the url and check if the incoming request
    is to be by passed or not.
    '''

    # Mention urls here that are not to be authenticated
    BYPASS_URLS = {
        '/user/login/',
        '/user/signup/'
    }
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            self.__authenticate_request(request)
        except Exception as e:
            return JsonResponse({
                "error": str(e)
            }, status=401)
        
        response = self.get_response(request)
        return response
    
    
    def __authenticate_request(self, request):
        if request.path in self.BYPASS_URLS:
            return
        
        payload = self.__get_payload(
            self.retrieve_access_token(request)
        )

        self.validate_user(payload, request)
        return True
    
    def __get_payload(self, jwt_token):
        try:
            return jwt.decode(
                jwt_token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature!')
        except:
            raise ParseError("Could not parse the token!")
