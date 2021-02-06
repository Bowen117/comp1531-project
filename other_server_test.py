'''
Imported files for other_server_test.
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
from datetime import datetime

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

def test_url(url):
    '''
    A simple sanity test to check that your server is set up properly
    '''
    assert url.startswith("http")

#################################################################################
#                                                                               #
#               users_all server testing functions                              #
#                                                                               #
#################################################################################

def test_user_all_valid(url):
    '''
    Testing if users_all works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    
    user_all_detail = requests.get(f"{url}/users/all?token={payload['token']}")
    payload2 = user_all_detail.json()
    
    print(payload2)
    assert user_all_detail.status_code == 200

    assert payload2['users'] == [{ 'u_id': 0,
                                    'email': 'ando@gmail.com',
                                    'name_first': 'ando',
                                    'name_last': 'pech',
                                    'handle_str': 'andopech',
                                    'profile_img_url': None,
                                },
                                {   'u_id': 1,
                                    'email': 'kiet@gmail.com',
                                    'name_first': 'kiet',
                                    'name_last': 'hoang',
                                    'handle_str': 'kiethoang',
                                    'profile_img_url': None,
                                },
                                {   'u_id': 2,
                                    'email': 'jenny@gmail.com',
                                    'name_first': 'jenny',
                                    'name_last': 'nguyen',
                                    'handle_str': 'jennynguyen',
                                    'profile_img_url': None,
                                }]

def test_user_all_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")

    requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    
    user_all_detail = requests.get(f"{url}/users/all?token={'invalid_token'}")

    assert user_all_detail.status_code == 400

#################################################################################
#                                                                               #
#               admin_userpermission_change server testing functions            #
#                                                                               #
#################################################################################

def test_permission_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")

    requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()
    requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    
    user_all_detail = requests.post(f"{url}/admin/userpermission/change", json={
        'token': 'invalid_token', 
        'u_id': payload2['u_id'], 
        'permission_id': 1
    })

    assert user_all_detail.status_code == 400

def test_permission_invalid_u_id(url):
    '''
    Testing when u_id is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    
    user_all_detail = requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload['token'], 
        'u_id': 1234123423, 
        'permission_id': 1
    })

    assert user_all_detail.status_code == 400

def test_permission_invalid_permission(url):
    '''
    Testing when permission is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()
    requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    
    user_all_detail = requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload['token'], 
        'u_id': payload2['u_id'], 
        'permission_id': 1234
    })

    assert user_all_detail.status_code == 400

def test_permission_non_owner_using_permission(url):
    '''
    Testing when a non-owner is using permission.
    '''
    requests.delete(f"{url}/clear")

    requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()
    auth2 = requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    payload3 = auth2.json()

    user_all_detail = requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload2['token'], 
        'u_id': payload3['u_id'], 
        'permission_id': 1
    })

    assert user_all_detail.status_code == 400

def test_permission_addowner(url):
    '''
    Testing if admin_userpermission_change works on server for adding an owner.
    '''
    requests.delete(f"{url}/clear")

    #flock owner
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()

    #change permissions to flock owner
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()

    #add as channel owner
    auth2 = requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    payload3 = auth2.json()

    #make user 2 become owner
    requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload['token'], 
        'u_id': payload2['u_id'], 
        'permission_id': 1
    })
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channel1', 
        'is_public': True
    })
    payload4 = channel_create.json()

    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id']
    })

    add = requests.post(f"{url}/channel/addowner", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id'], 
        'u_id': payload3['u_id']
    })
    channel_server_detail = requests.get(f"{url}/channel/details?token={payload['token']}&channel_id={payload4['channel_id']}")
    payload_detail = channel_server_detail.json()
    
    assert add.status_code == 200

    assert len(payload_detail['owner_members']) == 3
    assert payload_detail['owner_members'][0]['name_first'] == 'ando'
    assert payload_detail['owner_members'][1]['name_first'] == 'kiet'

def test_permissions_removeowner(url):
    '''
    Testing if admin_userpermission_change works on server for removing an owner.
    '''
    requests.delete(f"{url}/clear")

    #flock owner
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()

    #change permissions to flock owner
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()

    #add as channel owner
    auth2 = requests.post(f"{url}/auth/register", json={
        'email': 'jenny@gmail.com', 
        'password': 'password', 
        'name_first': 'jenny', 
        'name_last': 'nguyen'
    })
    payload3 = auth2.json()

    #make user 2 become owner
    requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload['token'], 
        'u_id': payload2['u_id'], 
        'permission_id': 1
    })
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channel1', 
        'is_public': True
    })
    payload4 = channel_create.json()

    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id']
    })

    add = requests.post(f"{url}/channel/addowner", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id'], 
        'u_id': payload3['u_id']
    })
    channel_server_detail = requests.get(f"{url}/channel/details?token={payload['token']}&channel_id={payload4['channel_id']}")
    payload_detail = channel_server_detail.json()
    
    assert add.status_code == 200

    assert len(payload_detail['owner_members']) == 3
    assert payload_detail['owner_members'][0]['name_first'] == 'ando'
    assert payload_detail['owner_members'][1]['name_first'] == 'kiet'

    remove = requests.post(f"{url}/channel/removeowner", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id'], 
        'u_id': payload3['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload['token']}&channel_id={payload4['channel_id']}")
    payload_detail2 = channel_server_detail.json()
    
    assert remove.status_code == 200

    assert len(payload_detail2['owner_members']) == 2
    assert payload_detail2['owner_members'][0]['name_first'] == 'ando'

def test_remove_flocker_owner_access(url):
    '''
    Testing for a valid message removed by a flockr owner.
    '''
    requests.delete(f"{url}/clear")

    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()

    #change permissions to flock owner
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channel1', 
        'is_public': True
    })
    payload4 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id']
    })
    
    raw = requests.post(f"{url}/message/send", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id'], 
        'message': "Hello world"
    })
    payload3 = raw.json()

    perms = requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload['token'], 
        'u_id': payload2['u_id'], 
        'permission_id': 1
    })

    assert perms.status_code == 200

    raw2 = requests.delete(f"{url}/message/remove", json={
        'token': payload2['token'], 
        'message_id': payload3['message_id']
    })

    assert raw2.status_code == 200
    
    search = requests.get(f"{url}/search?token={payload['token']}&query_str={'Hello world'}")
    payload6 = search.json()

    assert payload6['messages'] == []

def test_flocker_owner_access_other(url):
    '''
    Testing for a valid message edited by a flocker owner.
    '''
    requests.delete(f"{url}/clear")

    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()

    #change permissions to flock owner
    aug1 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'kiet', 
        'name_last': 'hoang'
    })
    payload2 = aug1.json()
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channel1', 
        'is_public': True
    })
    payload4 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id']
    })
    
    perms = requests.post(f"{url}/admin/userpermission/change", json={
        'token': payload['token'], 
        'u_id': payload2['u_id'], 
        'permission_id': 1
    })

    assert perms.status_code == 200

    raw = requests.post(f"{url}/message/send", json={
        'token': payload2['token'], 
        'channel_id': payload4['channel_id'], 
        'message': "Hello world"
    })
    payload3 = raw.json()

    raw1 = requests.put(f"{url}/message/edit", json={
        'token': payload2['token'], 
        'message_id': payload3['message_id'], 
        'message': "brownie"
    })

    assert raw1.status_code == 200

    search = requests.get(f"{url}/search?token={payload['token']}&query_str={'brownie'}")
    payload6 = search.json()

    assert payload6['messages'][0]['message'] == "brownie"

#################################################################################
#                                                                               #
#               search server testing functions                                 #
#                                                                               #
#################################################################################

def test_search_token_invalid(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channel1', 
        'is_public': True
    })
    payload4 = channel_create.json()
    
    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload4['channel_id'], 
        'message': "Hello world"
    })

    search = requests.get(f"{url}/search?token={'invalid'}&query_str={'brownie'}")

    assert search.status_code == 400

def test_search_valid(url):
    '''
    Testing if search works on server.
    '''
    requests.delete(f"{url}/clear")

    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channel1', 
        'is_public': True
    })
    payload4 = channel_create.json()
    
    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload4['channel_id'], 
        'message': "Hello world"
    })
    
    time_create_date = datetime.now().replace(microsecond=0)
    time_create_date.timestamp()

    search = requests.get(f"{url}/search?token={payload['token']}&query_str={'Hello world'}")
    payload6 = search.json()

    assert search.status_code == 200

    assert payload6['messages'][0]['message'] == 'Hello world'
    