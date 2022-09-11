import time
import uuid
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User , Transaction

# Create your views here.
def get_balance(username):
    balance = 0
    try: 
        result = Transaction.objects.filter( by=username )
        for item in result:
            if(item.type == "DEPOSIT"):
                balance += item.amount
            elif(item.type == "WITHDRAW"):
                balance -= item.amount
    except Exception as e:
        print(e)
        pass
    return balance

class InitView(APIView):
    def post(self, request, *args, **kwargs):
        content = {'status': 'failed'}
        customer_xid = request.POST.get('customer_xid', False)
        if customer_xid:
            try:
                user = User.objects.get(username=customer_xid)
                content = {'status': 'user ' + customer_xid + ' exist'}
            except User.DoesNotExist:
                user = User.objects.create_user(username= customer_xid , guid=str(uuid.uuid4()))
                content = {
                    "data": {
                        "token": Token.objects.create(user=user).key
                    },
                    "status": "success"
                }
                return Response(content)
        return Response(content)

class WalletIsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            return bool(True)
        return bool(request.user and request.user.is_authenticated and request.user.is_enabled)

class CustomIsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_enabled)

class WalletView(APIView):
    permission_classes = [WalletIsAuthenticated]
    def get(self, request, *args, **kwargs):
        now = time.time()
        content = { "status": "failed" , "message": "wait 5 sec or more" }
        user = request.user
        if( (now - user.last_check) > 5 ):
            user.last_check = now
            user.save()
            content = {
            "status": "success",
                "data": {
                    "wallet": {
                    "id": user.guid,
                    "owned_by": user.username,
                    "status": "enabled",
                    "enabled_at": datetime.utcfromtimestamp(user.enabled_at).strftime('%Y-%m-%dT%H:%M:%S') ,
                    "balance": get_balance(user.username)
                    }
                }
            }
        return Response(content)

    def post(self, request, *args, **kwargs):
        content = { "status": "failed" }

        user = request.user
        if user.is_enabled == False: 
            now = time.time()
            user.is_enabled = True
            user.enabled_at = now
            user.save()
            content = {
                "status": "success",
                "data": {
                    "wallet": {
                    "id": user.guid,
                    "owned_by": user.username,
                    "status": "enabled",
                    "enabled_at":datetime.utcfromtimestamp(now).strftime('%Y-%m-%dT%H:%M:%S'),
                    "balance": get_balance(user.username)
                    }
                }
            }
        return Response(content)

    def patch(self, request, *args, **kwargs):
        content = { "status": "failed" }
        is_disabled = request.POST.get('is_disabled', False)
        if(is_disabled == "true"):
            user = request.user
            if user.is_enabled == True: 
                now = time.time()
                user.is_enabled = False
                user.disabled_at = now
                user.save()
                content = {
                    "status": "success",
                    "data": {
                        "wallet": {
                        "id": user.guid,
                        "owned_by": user.username,
                        "status": "disabled",
                        "disabled_at":datetime.utcfromtimestamp(now).strftime('%Y-%m-%dT%H:%M:%S'),
                        "balance": get_balance(user.username)
                        }
                    }
                }
        return Response(content)

class DepositsView(APIView):
    permission_classes = [CustomIsAuthenticated]
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount', False)
        reference_id = request.POST.get('reference_id', False)

        content = { "status": "failed" }
        if reference_id and amount: 
            try:
                result = Transaction.objects.get(reference_id=reference_id) #.values_list('data', flat=True)
                content = { "status": "failed", "message": "reference_id exist" }
            except Transaction.DoesNotExist :
                now = time.time()
                guid = str(uuid.uuid4())
                result = Transaction.objects.create(guid=guid, timestamp=now , reference_id=reference_id , by=request.user.username , type="DEPOSIT" , amount=amount )
                content = {
                "status": "success",
                "data": {
                    "deposit": {
                        "id": guid,
                        "deposited_by": request.user.username,
                        "status": "success",
                        "deposited_at": datetime.utcfromtimestamp(now).strftime('%Y-%m-%dT%H:%M:%S'),
                        "amount": amount,
                        "reference_id": reference_id
                    }
                }
                }
                
        return Response(content)

class WithdrawalsView(APIView):
    permission_classes = [CustomIsAuthenticated]
    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount', False)
        reference_id = request.POST.get('reference_id', False)

        content = { "status": "failed" }
        if reference_id and amount: 
            try:
                result = Transaction.objects.get(reference_id=reference_id) #.values_list('data', flat=True)
                content = { "status": "failed", "message": "reference_id exist" }
            except Transaction.DoesNotExist :
                if( get_balance(request.user.username) >= int(amount) ):
                    now = time.time()
                    guid = str(uuid.uuid4())
                    result = Transaction.objects.create(guid=guid, timestamp=now , reference_id=reference_id , by=request.user.username , type="WITHDRAW" , amount=amount )
                    content = {
                    "status": "success",
                    "data": {
                        "deposit": {
                            "id": guid,
                            "deposited_by": request.user.username,
                            "status": "success",
                            "deposited_at": datetime.utcfromtimestamp(now).strftime('%Y-%m-%dT%H:%M:%S'),
                            "amount": amount,
                            "reference_id": reference_id
                        }
                    }
                    }
                else:
                    content = content = { "status": "failed", "message": "not enough balances" }
                
        return Response(content)