from rest_framework import serializers
from .models import Users, UserRole, Role
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class UserRegisterSerializer(serializers.ModelSerializer):
    role_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Users
        fields = ['username','email', 'phone', 'password', 'role_id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role_id = validated_data.pop('role_id', None)
        validated_data['password'] = make_password(validated_data['password'])
        # user = Users.objects.create(**validated_data)
        role = Role.objects.filter(id=role_id).first() if role_id else None

        # Create user with role assigned
        user = Users.objects.create(**validated_data, role=role)

        # Assign Role
        # if role_id:
        #     role = Role.objects.filter(id=role_id).first()
        #     if role:
        #         UserRole.objects.create(user=user, role=role)

        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False, allow_null=True) 
    class Meta:
        model = Users
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'profile_image', 'date_of_birth','address','role_id']