from django.db import models
from django.contrib.auth.models import AbstractUser
from shared.models import BaseModel
from datetime import datetime,timedelta
from django.core.validators import FileExtensionValidator
import random,uuid
from rest_framework_simplejwt.tokens import RefreshToken


# Create your models here.
ORDINARY_USER,MANAGER,ADMIN = ('ordinary_user','manager','admin')
VIA_EMAIL,VIA_PHONE = ('via_email','via_phone')
NEW,CODE_VERIFIED,DONE,PHOTO_STEP = ('new','code_verified','done','photo_step')

class User(AbstractUser,BaseModel):
    USER_ROLES = (
        (ORDINARY_USER,ORDINARY_USER),
        (MANAGER,MANAGER),
        (ADMIN,ADMIN)
    )
    AUTH_TYPES = (
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )
    AUTH_STATUS = (
        (NEW,NEW),
        (CODE_VERIFIED,CODE_VERIFIED),
        (DONE,DONE),
        (PHOTO_STEP,PHOTO_STEP)
    )
    user_roles = models.CharField(max_length=31,choices=USER_ROLES,default=ORDINARY_USER)
    auth_types = models.CharField(max_length=31,choices=AUTH_TYPES)
    auth_status = models.CharField(max_length=31,choices=AUTH_STATUS,default=NEW)
    email = models.EmailField(null=True,blank=True,unique=True)
    photo = models.ImageField(null=True,blank=True,upload_to='user_photos/',validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','heif','heic'])])
    phone_number = models.CharField(max_length=13,blank=True,null=True,unique=True)

    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def create_verify_code(self,verify_type):
        code = "".join([str(random.randint(0,100) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id = self.id,
            verify_type = verify_type,
            code = code
        )
        return code

    def check_username(self):
        if not self.username:
            temp_username = f"username - {uuid.uuid4.__str__().split('-')[-1]}"
            while User.objects.filter(username = temp_username):
                temp_username = f"{temp_username}{random.randint(0,9)}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f"password - {uuid.uuid4.__str__().split('-')[-1]}"
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            'access':str(refresh.access_token),
            'refresh_token':str(refresh)
        }
    
    def clean(self):
        self.check_username()
        self.check_email()
        self.check_pass()
        self.hashing_password()

    def save(self,*args,**kwargs):
        if not self.pk:
            self.clean()
        super(User,self).save(*args,**kwargs)

EMAIL_EXPIRE = 4
PHONE_EXPIRE = 2
class UserConfirmation(BaseModel):
    VERIFY_TYPE = (
        (VIA_EMAIL,VIA_EMAIL),
        (VIA_PHONE,VIA_PHONE)
    )
    verify_type = models.CharField(max_length=31,choices=VERIFY_TYPE)
    code = models.CharField(max_length=4)
    user = models.ForeignKey('users.User',on_delete=models.CASCADE,related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} was verified to access"
    
    def save(self,*args,**kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now()+timedelta(minutes=EMAIL_EXPIRE)
            else:
                self.expiration_time = datetime.now()+timedelta(minutes=PHONE_EXPIRE)
        super(UserConfirmation,self).save(*args,**kwargs)

    


    
