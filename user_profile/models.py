from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):

     def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)


    # Change the user manager
    objects = UserManager()

    # For making simplejwt choose email field for token generation
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def connections(self):
        ''' Connections for a user can be user1 or user2
        depending in which column does the user match.'''
        list1 = self.connection1.filter(status="accepted").values_list(
            'user2', flat=True
        )
        list2 = self.connection2.filter(status="accepted").values_list(
            'user1', flat=True
        )

        return User.objects.filter(pk__in=list(list1) + list(list2))
    
    @property
    def pending_requests(self):
        ''' Gives back the pending requests recieved by the user. '''
        requests_received = self.connection2.filter(status="pending")

        return requests_received
    
    @classmethod
    def search(cls, search_keyword):
        # If search keyword is an email, than exact matching.
        if '@' in search_keyword:
            return cls.objects.filter(
                email=search_keyword)
        
        return cls.objects.filter(
            first_name__icontains=search_keyword)
