from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.shortcuts import render
from .models import *

# Create your views here.
def register_views(request):
    if request.method.upper() == 'GET':
        uname = request.GET['username']
        user = User.objects.filter(uname=uname).first()
        if user:
            return HttpResponse('该用户名已被占用')
        else:
            return HttpResponse('&#12288;')

    else:
        uname = request.POST['username']
        upwd = request.POST['userpwd']
        uemail = request.POST.get('useremail')

        upwd = make_password(upwd,'Kmusic','pbkdf2_sha1')
        try:
            if uemail:
                user = User.objects.create(uname=uname,upwd=upwd,uemail=uemail)
            else:
                user = User.objects.create(uname=uname,upwd=upwd)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.uname
            return HttpResponse('ok')
        except:
            return HttpResponse('fail')


def logout_views(request):
    del request.session['user_id']
    del request.session['user_name']
    response = HttpResponse('logout ok')
    if request.COOKIES.get('user_id'):
        response.delete_cookie('user_id')
        response.delete_cookie('user_name')
    return response


def login_views(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        upwd = request.POST.get('upwd')
        isSave = request.POST.get('issave')
        if isSave == 'false':
            isSave = False
        user = User.objects.filter(uname=username).first()
        if user:
            if check_password(upwd,user.upwd):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.uname
                response = HttpResponse('ok')
                if isSave:
                    response.set_cookie('user_id', user.id)
                    response.set_cookie('user_name', user.uname)
                return response
            else:
                return HttpResponse('密码错误')
        else:
            return HttpResponse('无效的用户名')