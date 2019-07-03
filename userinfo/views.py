from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse

from .models import *

# Create your views here.
def register_views(request):
    if request.method.upper() == 'GET':
        username = request.GET['username']
        user = User.objects.filter(username=username).first()
        if user:
            return HttpResponse('该用户名已被占用')
        else:
            return HttpResponse('&#12288;')

    else:
        username = request.POST['username']
        password = request.POST['userpwd']
        email = request.POST.get('useremail','')

        try:
            user = User.objects.create(username=username,email=email)
            user.set_password(password)
            user.save()
            request.session['user_id'] = user.id
            request.session['user_name'] = user.username
            return HttpResponse('ok')
        except Exception as e:
            print(e)
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
        user = User.objects.filter(username=username).first()
        if user:
            if check_password(upwd,user.password):
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username
                response = HttpResponse('ok')
                if isSave:
                    response.set_cookie('user_id', user.id)
                    response.set_cookie('user_name', user.username)
                return response
            else:
                return HttpResponse('密码错误')
        else:
            return HttpResponse('无效的用户名')

