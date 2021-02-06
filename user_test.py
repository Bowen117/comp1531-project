'''
Imported files for user_test.
'''
import pytest
import error 
import user
import auth
from other import clear, users_all 
import json
from subprocess import Popen, PIPE
import re
import signal
from time import sleep
import requests


@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

#################################################################################
#                                                                               #
#                      user_profile testing functions                           #
#                                                                               #
#################################################################################

def test_wrong_u_id():
    '''
    Testing when u_id is invalid.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    with pytest.raises(error.InputError):
        user.user_profile(user_1.get('token'), 'invalid_u_id')

def test_profile_invalid_token():
    '''
    Testing when token is invalid.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    with pytest.raises(error.AccessError):
        user.user_profile('invalid_token', user_1.get('u_id'))

def test_profile_unregistered_user():
    '''
    Testing when user is unregistered.
    '''
    clear()
    with pytest.raises(error.AccessError):
        user.user_profile('invalid_token', "invalid_u_id")

def test_valid_user_profile():
    '''
    Testing if user_profile works.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    user_setemail = user.user_profile(user_1.get('token'), user_1.get('u_id'))
    assert user_setemail.get('user').get('u_id') == user_1.get('u_id')
    assert user_setemail['user']['email'] == "test_email1@gmail.com"
    assert user_setemail['user']['name_first'] == "User_1"
    assert user_setemail['user']['name_last'] == "User_last_1"
    assert user_setemail['user']['handle_str'] == "user_1user_last_1"
    assert user_setemail == {
                            'user' : {
                                'u_id': user_1.get('u_id'),
                                'email': "test_email1@gmail.com",
                                'name_first': "User_1",
                                'name_last': "User_last_1",
                                'handle_str': "user_1user_last_1",
                            }
                        }

def test_valid_user_profile2():
    '''
    Testing if user_profile works.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    user_setemail = user.user_profile(user_1.get('token'), user_1.get('u_id'))
    assert user_setemail == {
                            'user' : {
                                'u_id': user_1.get('u_id'),
                                'email': "test_email1@gmail.com",
                                'name_first': "User_1",
                                'name_last': "User_last_1",
                                'handle_str': "user_1user_last_1",
                            }
                        }


def test_valid_user_profile_handle3():
    '''
    Testing if handle is valid.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "donald", "Trump")
    user.user_profile_setname(user_1.get('token'), "Firstnamee", "Lastnamee")
    user.user_profile_sethandle(user_1.get('token'), 'NewHandle')
    user.user_profile_setemail(user_1.get('token'), "test2@gmail.com")
    user_setemail = user.user_profile(user_1.get('token'), user_1.get('u_id'))

    assert user_setemail.get('user').get('u_id') == user_1.get('u_id')
    assert user_setemail['user']['email'] == "test2@gmail.com"
    assert user_setemail['user']['name_first'] == "Firstnamee"
    assert user_setemail['user']['name_last'] == "Lastnamee"
    assert user_setemail['user']['handle_str'] == "NewHandle"

#################################################################################
#                                                                               #
#                      user_profile_setemail testing functions                  #
#                                                                               #
#################################################################################

def test_invalid_email():
    '''
    Testing when email is invalid.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    with pytest.raises(error.InputError):
        user.user_profile_setemail(user_1.get('token'), 'invalid_email')

def test_sameinvalid_email():
    '''
    Testing when email is invalid.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    with pytest.raises(error.InputError):
        user.user_profile_setemail(user_1.get('token'), 'test_email1@gmail.com')

def test_invalid_email_token():
    '''
    Testing when token is invalid.
    '''
    clear()
    auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    with pytest.raises(error.AccessError):
        user.user_profile_setemail('token', "ando@gmail.com")
 
def test_already_used_email():
    '''
    Testing when updated email is already being used.
    '''
    clear()
    user_1 = auth.auth_register("test_email2@gmail.com", "passwordone", "User_1", "User_last_1") 
    with pytest.raises(error.InputError):
        user.user_profile_setemail(user_1.get('token'), 'test_email2@gmail.com')

def test_invalid_token():
    '''
    Testing when token is invalid.
    '''
    clear()
    user_1 = auth.auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    with pytest.raises(error.AccessError):
        user.user_profile_setemail('invalid_token', user_1.get('email'))

def test_unregistered_user():
    '''
    Testing when user is unregistered.
    '''
    clear()
    with pytest.raises(error.AccessError):
        user.user_profile('invalid_token', 'invalid_u_id')

def test_if_working_user():
    '''
    Testing if user_profile_setemail works.
    '''
    clear()
    user_1 = auth.auth_register("test_email2@gmail.com", "passwordone", "User_1", "User_last_1")
    user_token = user_1.get("token")
    user.user_profile_setemail(user_token, "test@gmail.com")
    email = user.user_profile(user_token, user_1.get("u_id")).get("user").get("email")
    assert email == "test@gmail.com"

def test_if_working_user3():
    '''
    Testing if user_profile_setemail works.
    '''
    clear()
    user_1 = auth.auth_register("test_email2@gmail.com", "passwordone", "User_1", "User_last_1")
    user_token = user_1.get("token")
    user.user_profile_setemail(user_token, "test222@gmail.com")
    email = user.user_profile(user_token, user_1.get("u_id")).get("user").get("email")
    assert email == "test222@gmail.com"

#################################################################################
#                                                                               #
#                 user_profile_setname testing functions                        #
#                                                                               #
#################################################################################

def test_setname_name_too_long():
    '''
    Testing when the first name is too long.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    with pytest.raises(error.InputError):
        user.user_profile_setname(user_token, "a"*100, "password")

def test_setname_name_too_short():
    '''
    Testing when the first name is too short.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    with pytest.raises(error.InputError):
        user.user_profile_setname(user_token, "", "ggggggggggg")

def test_lastname_name_too_short():
    '''
    Testing when the last name is too short.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    with pytest.raises(error.InputError):
        user.user_profile_setname(user_token, "wendy", "")

def test_lastname_name_too_long():
    '''
    Testing when the last name is too long.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    with pytest.raises(error.InputError):
        user.user_profile_setname(user_token, "will", "a"*100)

def test_token_setname():
    '''
    Testing when the token is invalid.
    '''
    clear()
    auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    with pytest.raises(error.AccessError):
        user.user_profile_setname("invalid", "Eren", "ggggggggggg")

def test_setname_empty():
    '''
    Testing when first and last name is empty.
    '''
    clear()
    with pytest.raises(error.AccessError):
        user.user_profile_setname("user_token", "", "")

def test_setname_invalid_token_2():
    '''
    Testing when token is invalid.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_id = user_1.get("u_id")
    with pytest.raises(error.AccessError):
        user.user_profile('invalid_token', user_id)

def test_setname_working():
    '''
    Testing if user_profile_setname works.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    user_id = user_1.get("u_id")
    return_user = user.user_profile_setname(user_token, "Firstnamee", "Lastnamee")
    assert return_user == {}
    profile_user = user.user_profile(user_token, user_id) 
    assert profile_user['user']['name_first'] == "Firstnamee"
    assert profile_user['user']['name_last'] == "Lastnamee"

def test_returnsetname_working():
    '''
    Testing if user_profile_setname works.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    user_1.get("u_id")
    returnuser = user.user_profile_setname(user_token, "Firstnamee", "Lastnamee")
    assert returnuser == {}

def test_invalid_name_first_50():
    """
    testing edge case with name 50 chars long
    """
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    user_1.get("u_id")
    with pytest.raises(error.InputError):
        user.user_profile_setname(user_token, "a"*51, "Lastnamee")


def test_setname_working3():
    '''
    Testing if user_profile_setname works.
    '''
    clear()
    user_1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_1.get("token")
    user_id = user_1.get("u_id")
    return_user = user.user_profile_setname(user_token, "Firstnamee", "Lastnamee")
    assert return_user == {}
    profile_user = user.user_profile(user_token, user_id) 
    assert profile_user['user']['name_first'] == "Firstnamee"
    assert profile_user['user']['name_last'] == "Lastnamee"

    user_2 = auth.auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user_token = user_2.get("token")
    user_id = user_2.get("u_id")
    return_user = user.user_profile_setname(user_token, "www", "eee")
    assert return_user == {}
    profile_user = user.user_profile(user_token, user_id) 
    assert profile_user['user']['name_first'] == "www"
    assert profile_user['user']['name_last'] == "eee"

    user_token = user_1.get("token")
    user_id = user_1.get("u_id")
    return_user = user.user_profile_setname(user_token, "ando", "ewewe")
    assert return_user == {}
    profile_user = user.user_profile(user_token, user_id) 
    assert profile_user['user']['name_first'] == "ando"
    assert profile_user['user']['name_last'] == "ewewe"

    user_token = user_2.get("token")
    user_id = user_1.get("u_id")
    return_user = user.user_profile_setname(user_token, "ando", "ewewe")
    assert return_user == {}
    profile_user = user.user_profile(user_token, user_id) 
    assert profile_user['user']['name_first'] == "ando"
    assert profile_user['user']['name_last'] == "ewewe"

#################################################################################
#                                                                               #
#                 user_profile_sethandle testing functions                      #
#                                                                               #
#################################################################################

def test_handle_str_invalid_1():
    '''
    Testing when the string is invalid.
    '''
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")

    with pytest.raises(error.InputError):
        user.user_profile_sethandle(user_token, '2')

def test_handle_str_invalid_token():
    '''
    Testing when the token is invalid.
    '''
    clear()
    auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")

    with pytest.raises(error.AccessError):
        user.user_profile_sethandle("invalid", 'newhandel')

def test_handle_str_invalid_2():
    '''
    Testing when the string is invalid.
    '''
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")

    with pytest.raises(error.InputError):
        user.user_profile_sethandle(user_token, 'Thisismorethantwentycharacterslong')

def test_handle_already_being_used():
    '''
    Testing when the handle is already being used by another user.
    '''
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")
    user.user_profile_sethandle(user_token, 'NewHandle')
    
    user2 = auth.auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user_token2 = user2.get("token")
    with pytest.raises(error.InputError):
        user.user_profile_sethandle(user_token2, 'NewHandle')

def test_handle_str_working():
    '''
    Testing if user_profile_sethandle works.
    '''
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")
    user_id = user1.get("u_id")
    test_return = user.user_profile_sethandle(user_token, 'NewHandle')
    assert test_return == {}
    details = user.user_profile(user_token, user_id)
    handle = details.get('user').get("handle_str")
    assert handle == "NewHandle"

def test_handle_str_working_2():
    '''
    Testing if user_profile_sethandle works.
    '''
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")
    user_id = user1.get("u_id")
    user.user_profile_sethandle(user_token, 'btx')
    details = user.user_profile(user_token, user_id)
    handle = details.get('user').get("handle_str")
    assert handle == "btx"

    user.user_profile_sethandle(user_token, 'eren')
    details = user.user_profile(user_token, user_id)
    handle = details.get('user').get("handle_str")
    assert handle == "eren"

#################################################################################
#                                                                               #
#                 user_profile_uploadphoto testing functions                    #
#                                                                               #
#################################################################################

def test_uploadphoto_dimension_out_of_bounds():
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")
    
    profile_url = "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg"

    with pytest.raises(error.InputError):
        user.user_profile_uploadphoto(user_token, profile_url, 0, 0, 10000, 10000)

def test_uploadphoto_invalid_token():
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user1.get("token")
    
    profile_url = "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg"

    with pytest.raises(error.AccessError):
        user.user_profile_uploadphoto('invalid_token', profile_url, 0, 0, 200, 200)

def test_uploadphoto_not_jpg():
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")
    
    profile_url = "https://static.wixstatic.com/media/2cd43b_5588a2ed6ccc49b3b2a2bb32ec4231d1~mv2.png/v1/fill/w_250,h_250,fp_0.50_0.50/2cd43b_5588a2ed6ccc49b3b2a2bb32ec4231d1~mv2.png"
    with pytest.raises(error.InputError):
        user.user_profile_uploadphoto(user_token, profile_url, 0, 0, 100, 100)

def test_invalid_url():
    clear()
    user1 = auth.auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user1.get("token")
    
    with pytest.raises(error.InputError):
        user.user_profile_uploadphoto(user_token, "invalid", 0, 0, 100, 100)

def test_uploadphoto_normal(url):

    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    
    a = requests.post(f"{url}/user/profile/uploadphoto", json={
        'token': payload['token'],
        'img_url': "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg",
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300,
    })
    payload2 = a.json()
    assert payload2 == {}
    payload3 = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    profile3 = payload3.json()
    assert payload3.status_code == 200


    assert profile3 == {
                        'user' : {
                            'u_id': payload.get('u_id'),
                            'email': "ando@gmail.com",
                            'name_first': "ando",
                            'name_last': "pech",
                            'handle_str': "andopech",
                            'profile_img_url': f'{url}static/0.jpg',
                        }
                    }                        

def test_uploadphoto_error_token(url):

    requests.delete(f"{url}/clear")
    
    requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = requests.post(f"{url}/user/profile/uploadphoto", json={
        'token': 'token',
        'img_url': "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg",
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300,
    })

    assert payload.status_code == 400

def test_uploadphoto_error_url(url):

    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    token = auth_reg.json()

    payload = requests.post(f"{url}/user/profile/uploadphoto", json={
        'token': token['token'],
        'img_url': "ww",
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300,
    })

    assert payload.status_code == 400

def test_uploadphoto_error_jpeg(url):

    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    token = auth_reg.json()

    payload = requests.post(f"{url}/user/profile/uploadphoto", json={
        'token': token['token'],
        'img_url': "https://static.wixstatic.com/media/2cd43b_5588a2ed6ccc49b3b2a2bb32ec4231d1~mv2.png/v1/fill/w_250,h_250,fp_0.50_0.50/2cd43b_5588a2ed6ccc49b3b2a2bb32ec4231d1~mv2.png",
        'x_start': 0,
        'y_start': 0,
        'x_end': 300,
        'y_end': 300,
    })
    assert payload.status_code == 400
    

def test_uploadphoto_error_size1(url):

    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    token = auth_reg.json()

    payload = requests.post(f"{url}/user/profile/uploadphoto", json={
        'token': token['token'],
        'img_url': "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg",
        'x_start': 0,
        'y_start': 0,
        'x_end': 3000,
        'y_end': 300,
    })

    assert payload.status_code == 400

def test_uploadphoto_error_size2(url):

    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    token = auth_reg.json()

    payload = requests.post(f"{url}/user/profile/uploadphoto", json={
        'token': token['token'],
        'img_url': "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg",
        'x_start': 0,
        'y_start': 0,
        'x_end': 10000,
        'y_end': 300,
    })

    assert payload.status_code == 400
    