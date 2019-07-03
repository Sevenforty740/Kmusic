def jwt_response_username_userid_token(token,user=None,request=None):
    '''
    JWT登入验证成功之后 ，自定义处理返回数据
    :param token:
    :param user:
    :param request:
    :return:
    '''

    data = {
        'token':token,
        'username':user.username,
        'user_id':user.id,
        'regist_time':user.last_login
    }
    return data
