'''
Imported files for user_server_test.
'''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep

import requests
import json
import auth
import channels
import channel
import other
import message
import user

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
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
#                             User profile test                                 #
#                                                                               #
#################################################################################
def test_user_profile_valid(url):
    '''
    Test if profile works
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
 
    requests.put(f"{url}/user/profile/sethandle", json = {'token': payload['token'], 'handle_str': 'Newhandle'})
    profile = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    user_profile_details = profile.json()
    payload2 = user_profile_details.get('user')
  
    assert profile.status_code == 200
    assert payload2['email'] == 'ando@gmail.com'
    assert payload2['u_id'] == payload['u_id']
    assert payload2['name_first'] == 'ando'
    assert payload2['name_last'] == 'pech'
    assert payload2['handle_str'] == 'Newhandle'


def test_user_profile_token_invalid(url):
    '''
    Test if token valid
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
 
    profile = requests.get(f"{url}/user/profile?token=invalid&u_id={payload['u_id']}")
    assert profile.status_code == 400


def test_user_profile_token_u_id(url):
    '''
    Test u_id error
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
 
    profile = requests.get(f"{url}/user/profile?token={payload['token']}&u_id=1")
    assert profile.status_code == 400


#################################################################################
#                                                                               #
#                             user set name test                                #
#                                                                               #
#################################################################################
def test_user_setname_working(url):
    '''
    Test if the function and interface works
    '''
    requests.delete(f"{url}/clear")

    return_auth = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = return_auth.json()
    payload2 = requests.put(f"{url}/user/profile/setname", json = {'token': payload['token'], 'name_first': 'Donald', 'name_last': 'Trump'})
    assert payload2.status_code == 200 

    payload3 = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    profile = payload3.json().get('user')
    assert profile['name_first'] == 'Donald'
    assert profile['name_last'] == 'Trump'

def test_user_setname_errors(url): 
    '''
    Test errors, token invalid
    '''
    requests.delete(f"{url}/clear")
    requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload2 = requests.put(f"{url}/user/profile/setname", json = {'token': 'token', 'name_first': 'Donald', 'name_last': 'Trump'})
    assert payload2.status_code == 400

def test_user_setname_errors_firstname(url): 
    '''
    Test errors firstname too long
    '''
    requests.delete(f"{url}/clear")
    requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload2 = requests.put(f"{url}/user/profile/setname", json = {'token': 'token', 'name_first': 'a'*100, 'name_last': 'Trump'})
    assert payload2.status_code == 400


def test_user_setname_errors_lastname(url): 
    '''
    Test errors last name too long

    '''
    requests.delete(f"{url}/clear")
    requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload2 = requests.put(f"{url}/user/profile/setname", json = {'token': 'token', 'name_first': 'abc', 'name_last': 'Trump'*100})
    assert payload2.status_code == 400

#################################################################################
#                                                                               #
#                             user set handle test                              #
#                                                                               #
#################################################################################

def test_user_sethandle_works(url):
    '''
    Test if sethandle flask works
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    payload2 = requests.put(f"{url}/user/profile/sethandle", json = {'token': payload['token'], 'handle_str': 'NewHandle'})
    payload2.status_code == 200 
    profile = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    user_profile_details = profile.json()
    payload3 = user_profile_details.get('user')
    assert payload3['handle_str'] == 'NewHandle'

def test_user_sethandle_token_error(url):
    '''
    Test token error
    '''
    requests.delete(f"{url}/clear")
    requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload2 = requests.put(f"{url}/user/profile/sethandle", json = {'token': 'token', 'handle_str': 'NewHandle'})
    payload2.status_code == 400

def test_user_sethandle_handle_error_toolong(url):
    '''
    Test token error
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    payload2 = requests.put(f"{url}/user/profile/sethandle", json = {'token': payload['token'], 'handle_str': 'a'*21})
    payload2.status_code == 400

def test_user_sethandle_handle_error_tooshort(url):
    '''
    Test token error
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    payload2 = requests.put(f"{url}/user/profile/sethandle", json = {'token': payload['token'], 'handle_str': 'a'})
    payload2.status_code == 400

#################################################################################
#                                                                               #
#                             user set email test                               #
#                                                                               #
#################################################################################

def test_user_email_works(url):
    '''
    Test if email works
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    email = requests.put(f"{url}/user/profile/setemail", json = {'token': payload['token'], 'email': 'newemail@gmail.com'})
    assert email.status_code == 200 
    profile = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    user_profile_details = profile.json()
    payload3 = user_profile_details.get('user')
    assert payload3['email'] == 'newemail@gmail.com'

def test_user_email_token_invalid(url):
    '''
    Test if token invalid returns error
    '''
    requests.delete(f"{url}/clear")
    requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    email = requests.put(f"{url}/user/profile/setemail", json = {'token': 'token', 'email': 'newemail@gmail.com'})
    assert email.status_code == 400

def test_user_email_email_invalid(url):
    '''
    Test if invalid email returns error
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    email = requests.put(f"{url}/user/profile/setemail", json = {'token': payload['token'], 'email': 'newemail'})
    assert email.status_code == 400

def test_user_email_same_invalid(url):
    '''
    Test if same email returns error
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    requests.put(f"{url}/user/profile/setemail", json = {'token': payload['token'], 'email': 'newemail@gmail.com'})
    email = requests.put(f"{url}/user/profile/setemail", json = {'token': payload['token'], 'email': 'newemail@gmail.com'})
    assert email.status_code == 400


#################################################################################
#                                                                               #
#                      user_upload set email test                               #
#                                                                               #
#################################################################################

def test_uploadphoto_dimension_out_of_bounds(url):
    '''
    Test if invalid out of bounds
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    
    profile_url = "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg"

    photo = requests.post(f"{url}/user/profile/uploadphoto", json = {'token': payload['token'], 'img_url': profile_url, 'x_start': 0, 'y_start': 0,'x_end': 20000, 'y_end': 20000})
    
    assert photo.status_code == 400

def test_uploadphoto_invalid_token(url):
    '''
    Test if invalid token returns error
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    auth_reg_return.json()
    
    profile_url = "https://thumbs.dreamstime.com/b/mallard-duck-closeup-profile-portrait-male-mallard-duck-closeup-profile-portrait-calm-pond-168218987.jpg"

    photo = requests.post(f"{url}/user/profile/uploadphoto", json = {'token': 'invalid_token', 'img_url': profile_url, 'x_start': 0, 'y_start': 0,'x_end': 200, 'y_end': 200})
    
    assert photo.status_code == 400

def test_uploadphoto_not_jpg(url):
    '''
    Test if not valid file type
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()
    
    profile_url = "https://purepng.com/public/uploads/large/31506353022itpjqwgn1xwrzlpejk5qgfwycjc6j80kdzsp3jqlgcvzm412riv59y4tpu0uf8oij5ato7jllyst8bsudyzxudsrugibonrghkya.png"

    photo = requests.post(f"{url}/user/profile/uploadphoto", json = {'token': payload['token'], 'img_url': profile_url, 'x_start': 0, 'y_start': 0,'x_end': 200, 'y_end': 200})
    
    assert photo.status_code == 400

def test_invalid_url(url):
    '''
    Test if invalid url
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json = {'email': 'ando@gmail.com', 'password': 'password', 'name_first': 'ando', 'name_last': 'pech'})
    payload = auth_reg_return.json()

    photo = requests.post(f"{url}/user/profile/uploadphoto", json = {'token': payload['token'], 'img_url': 'url_invalid', 'x_start': 0, 'y_start': 0,'x_end': 200, 'y_end': 200})
    
    assert photo.status_code == 400