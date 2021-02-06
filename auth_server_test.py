'''
Imported files for auth_server_test.
'''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests
import pytest

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

def test_echo(url):
    '''
    A simple test to check echo
    '''
    resp = requests.get(url + 'echo', params={'data': 'hello'})
    assert json.loads(resp.text) == {'data': 'hello'}

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    assert url.startswith("http")

#################################################################################
#                                                                               #
#                      auth_register server testing functions                   #
#                                                                               #
#################################################################################

def test_register_valid(url):
    '''
    Testing if auth_register works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })
    payload = auth_reg_return.json()
    
    user_server_detail = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    payload2 = user_server_detail.json()
    
    assert user_server_detail.status_code == 200
    assert payload2['user']['u_id'] == payload['u_id']
    assert payload2['user']['email'] == "abc@gmail.com"

def test_register_invalid_email(url):
    '''
    Testing when email is invalid.
    '''
    requests.delete(f"{url}/clear")

    raw = requests.post(f"{url}/auth/register", json={
        'email': 'abc', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })

    assert raw.status_code == 400

def test_register_invalid_password(url):
    '''
    Testing when password is invalid.
    '''
    requests.delete(f"{url}/clear")

    raw = requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'pass', 
        'name_first': 'abc', 
        'name_last': 'def'
    })

    assert raw.status_code == 400

#################################################################################
#                                                                               #
#                      auth_logout server testing functions                     #
#                                                                               #
#################################################################################

def test_logout_valid(url):
    '''
    Testing if auth_logout works on server.
    '''
    requests.delete(f"{url}/clear")
    
    r = requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })
    payload = r.json()

    logout_return = requests.post(f"{url}/auth/logout", json={'token': payload['token']})
    payload2 = logout_return.json()

    assert logout_return.status_code == 200
    assert payload2['is_success'] == True

def test_logout_invalid(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })

    logout_return = requests.post(f"{url}/auth/logout", json={'token': 'invalid_token'})
    payload2 = logout_return.json()

    assert payload2['is_success'] == False

#################################################################################
#                                                                               #
#                      auth_login server testing functions                      #
#                                                                               #
#################################################################################

def test_login_valid(url):
    '''
    Testing if auth_login works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })
    payload = auth_reg_return.json()
    
    user_server_detail = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    payload2 = user_server_detail.json()
    
    assert payload2['user']['u_id'] == payload['u_id']
    assert payload2['user']['email'] == "abc@gmail.com"

    logout_return = requests.post(f"{url}/auth/logout", json={'token': payload['token']})
    payload3 = logout_return.json()

    assert payload3['is_success'] == True

    login_return = requests.post(f"{url}/auth/login", json={
        'email': payload2['user']['email'], 
        'password': 'password'
    })
    payload4 = login_return.json()
    
    assert login_return.status_code == 200
    assert payload2['user']['u_id'] == payload4['u_id']
    assert payload2['user']['email'] == "abc@gmail.com"

def test_login_invalid_password(url):
    '''
    Testing when password is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })
    payload = auth_reg_return.json()
    
    user_server_detail = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    payload2 = user_server_detail.json()
    
    assert payload2['user']['u_id'] == payload['u_id']
    assert payload2['user']['email'] == "abc@gmail.com"

    logout_return = requests.post(f"{url}/auth/logout", json={'token': payload['token']})
    payload3 = logout_return.json()

    assert payload3['is_success'] == True

    login_return = requests.post(f"{url}/auth/login", json={
        'email': payload2['user']['email'], 
        'password': 'passwordddddd'
    })
    
    assert login_return.status_code == 400

def test_login_invalid_email(url):
    '''
    Testing when email is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'abc@gmail.com', 
        'password': 'password', 
        'name_first': 'abc', 
        'name_last': 'def'
    })
    payload = auth_reg_return.json()
    
    user_server_detail = requests.get(f"{url}/user/profile?token={payload['token']}&u_id={payload['u_id']}")
    payload2 = user_server_detail.json()
    
    assert payload2['user']['u_id'] == payload['u_id']
    assert payload2['user']['email'] == "abc@gmail.com"

    logout_return = requests.post(f"{url}/auth/logout", json={'token': payload['token']})
    payload3 = logout_return.json()

    assert payload3['is_success'] == True

    login_return = requests.post(f"{url}/auth/login", json={
        'email': 'email@gmail', 
        'password': 'password'
    })
    
    assert login_return.status_code == 400

#################################################################################
#                                                                               #
#               auth_passwordreset_request server testing functions             #
#                                                                               #
#################################################################################
'''
Testing when email is unregistered
'''
def test_request_invalid_email(url):
    requests.delete(f"{url}/clear")

    request_reset = requests.post(f"{url}/auth/passwordreset/request", json={
        'email': 'unregistered@gmail.com'
    })

    assert request_reset.status_code == 400

'''
Testing a working request
'''
def test_request_working(url):
    requests.delete(f"{url}/clear")

    requests.post(f"{url}/auth/register", json={
        'email': 'fridaygrape1@gmail.com', 
        'password': 'password', 
        'name_first': 'friday', 
        'name_last': 'grape'
    })

    request_reset = requests.post(f"{url}/auth/passwordreset/request", json={
        'email': 'fridaygrape1@gmail.com'
    })

    assert request_reset.status_code == 200

'''
Testing multiple working requests
'''
def test_request_working_multiple_requests(url):
    requests.delete(f"{url}/clear")

    requests.post(f"{url}/auth/register", json={
        'email': 'fridaygrape1@gmail.com', 
        'password': 'password', 
        'name_first': 'friday', 
        'name_last': 'grape'
    })

    request_reset = requests.post(f"{url}/auth/passwordreset/request", json={
        'email': 'fridaygrape1@gmail.com'
    })
    request_reset = requests.post(f"{url}/auth/passwordreset/request", json={
        'email': 'fridaygrape1@gmail.com'
    })

    assert request_reset.status_code == 200

#################################################################################
#                                                                               #
#               auth_passwordreset_reset server testing functions               #
#                                                                               #
#################################################################################
'''
Testing an invalid reset code
'''
def test_reset_invalid_resetcode(url):
    requests.delete(f"{url}/clear")

    requests.post(f"{url}/auth/register", json={
        'email': 'fridaygrape1@gmail.com', 
        'password': 'password', 
        'name_first': 'friday', 
        'name_last': 'grape'
    })

    requests.post(f"{url}/auth/passwordreset/request", json={
        'email': 'fridaygrape1@gmail.com'
    })

    password_reset = requests.post(f"{url}/auth/passwordreset/reset", json={
        'reset_code': '12321',
        'new_password': 'newpassword'
    })

    assert password_reset.status_code == 400
