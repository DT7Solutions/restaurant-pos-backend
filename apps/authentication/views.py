from django.shortcuts import render

# Create your views here.
import json
from django.contrib.auth import authenticate,get_user_model
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from apps.authentication.utils import *
from .models import Users
from .serializers import *
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions

from rest_framework_simplejwt.views import TokenObtainPairView
# method apis 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
# from django.core.mail import send_mail

from django.http import JsonResponse

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        # Check if email exists
        if User.objects.filter(email=data.get('email')).exists():
            return Response({'message': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if username exists
        if User.objects.filter(username=data.get('username')).exists():
            return Response({'message': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if phone number exists (Assuming you have a `phone_number` field)
        if User.objects.filter(phone=data.get('phone')).exists():
            return Response({'message': 'Phone number already exists'}, status=status.HTTP_400_BAD_REQUEST)

        # Proceed with serializer
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(email=email, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful',
                'role': user.role.role_category if user.role else None, 
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer
 
    def get_object(self):
        return self.request.user
    
    def get(self, request, *args, **kwargs):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        user = request.user
        mutable_data = request.data.copy()

        flat_data = {key: value[0] if isinstance(value, list) else value for key, value in mutable_data.lists()}

        for key in ['profile_image', 'date_of_birth', 'pincode', 'address','city','district','state']:
            if flat_data.get(key) == 'null':
                flat_data[key] = None

        if flat_data.get('pincode'):
            try:
                flat_data['pincode'] = int(flat_data['pincode'])
            except ValueError:
                return Response({'pincode': ['Must be a valid number.']}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(user, data=flat_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            print(serializer.errors) 
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request, user_id):
  
    if not user_id:
        return Response({"error": "User ID is required"}, status=400)
    
    try:
        user = Users.objects.get(id=user_id)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=200)
    except Users.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_otp(request,user_id):
    if request.method == "POST":
        try:
            user_Id = user_id

            if not user_Id:
                return JsonResponse({"error": "User ID is required"}, status=400)
        
            oUser = Users.objects.get(id=user_id)
            otp_code = generate_otp()
            user_email = oUser.email
            send_otp_email(user_email, otp_code)
            oUser.otp = otp_code
            oUser.save()
          
            return JsonResponse({"message": "OTP sent registered email!"}, status=200)

        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp_change_password(request):
    if request.method == "POST":
        try:
            enter_otp = request.data["otp"]
            user_Id = request.data["user_id"]
            password = request.data["password"]

            if not user_Id:
                return JsonResponse({"error": "User ID is required"}, status=400)
            
            oUser = Users.objects.get(id=user_Id)
            if oUser.otp == int(enter_otp):
                oUser.password = make_password(password)
                oUser.save()
                return JsonResponse({"success": True, "message": "Password updated successfully!"}, status=200)
            else:
                return JsonResponse({"success": False, "message": "Invalid OTP"}, status=400)

        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
@api_view(["POST"])
def request_password_reset(request):
    email = request.data.get("email")
   
    if not email:
        return JsonResponse({"error": "email is required "}, status=400)
        
    try:
        oUser = Users.objects.get(email=email)
        otp_code = generate_otp()
        send_otp_email(oUser.email, otp_code)
        oUser.otp = otp_code
        oUser.save()

        return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

    except Users.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

# Step 2: Verify OTP
@csrf_exempt
@api_view(["POST"])
def verify_otp_forgot_password(request):
    email = request.data.get("email")
    otp = request.data.get("otp")
    try: 
        oUser = Users.objects.get(email=email)
        if oUser.otp == int(otp):
            return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
    except Users.DoesNotExist:
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def forgot_change_password(request):
    if request.method == "POST":
        try:
           
            emailid = request.data["email"]
            password = request.data["password"]

            if not emailid:
                return JsonResponse({"error": "User email id is required"}, status=400)
            
            oUser = Users.objects.get(email=emailid)
            if oUser:
                oUser.password = make_password(password)
                oUser.save()
                return JsonResponse({"success": True, "message": "Password updated successfully!"}, status=200)
            return Response({"message": "Password updated fail!."}, status=status.HTTP_400_BAD_REQUEST)
        except Users.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)

@api_view(['POST'])
def mobial_otp_request(request):
    try:
        phone = request.data['phone_number']
        if not phone:
            return JsonResponse({'error': 'Mobile number is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = Users.objects.get(phone=phone, is_active=True)
        if user:
           
            otp_code = generate_otp()
            user.otp = otp_code
            user.save()

            print(otp_code)
            
            # send_mobial_otp(phone,otp_code)
            return JsonResponse({"success": True,'message': 'OTP Sent. Register Phone number successfully!','user_id':user.Id}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({'error': 'User not found or inactive'}, status=status.HTTP_400_BAD_REQUEST)

    except Users.DoesNotExist:
        return JsonResponse({'error': 'Phone number does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['POST'])
def verify_mobial_otp(request):
        try:
            phone_number = request.data['phone_number']
            otp = request.data['otp']

            user = Users.objects.get(phone=phone_number, is_active=True)
            if user:
                if user.otp == int(otp):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'message': 'Login successful'
                    }, status=status.HTTP_200_OK)
                
                    return JsonResponse({"success": True, "message": "OTP verified successfully."})
                else:
                    return JsonResponse({"success": False, "message": "Invalid OTP."}, status=400)
            else:
                return JsonResponse({'error': 'User not found or inactive'}, status=status.HTTP_400_BAD_REQUEST)

        except Users.DoesNotExist:
             return JsonResponse({'error': 'Phone number does not exist'}, status=status.HTTP_404_NOT_FOUND)