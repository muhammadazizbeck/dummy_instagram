from rest_framework import serializers
from .models import User,VIA_EMAIL,VIA_PHONE,NEW,CODE_VERIFIED,DONE,PHOTO_STEP
from shared.utility import check_email_or_phone
from rest_framework.exceptions import ValidationError

class SignUpSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self,*args,**kwargs):
        super(SignUpSerializer,self).__init__(*args,**kwargs)
        self.fields['email_phone_number'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('id','auth_types','auth_status')
        extra_kwargs = {
            'auth_types':{'read_only':True,'required':False},
            'auth_status':{'read_only':True,'required':False}
        }
    
    def create(self, validated_data):
        auth_types = validated_data.pop('auth_type', None)
        user = User.objects.create(**validated_data)
        print(user)

        if user.auth_types == VIA_EMAIL:
            code = user.create_verify_code(VIA_EMAIL)
            print(code)
        elif user.auth_types == VIA_PHONE:
            code = user.create_verify_code(VIA_PHONE)
            print(code)

        user.save()
        return user

    
    
    def validate(self, data):
        super(SignUpSerializer,self).validate(data)
        data = self.auth_validate(data)
        return data
        
    @staticmethod
    def auth_validate(data):
        print(data)
        user_input = str(data.get('email_phone_number')).lower()
        input_type = check_email_or_phone(user_input)
        if input_type == 'email':
            data = {
                'email':user_input,
                'auth_type':VIA_EMAIL
            }
        elif input_type =='phone':
            data = {
                'phone':user_input,
                'auth_type':VIA_PHONE
            }
        else:
            data = {
                'success':False,
                'message':'You must send email or phone number'
            }
            raise ValidationError(data)
        print('data',data)
        return data
    



