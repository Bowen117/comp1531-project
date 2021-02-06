'''
Imported files for channel_server_test.
'''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests

import channels
import channel
import other

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
#                      channel_invite server testing functions                  #
#                                                                               #
#################################################################################

def test_channel_invite_valid(url):
    '''
    Testing if channel_invite works on server.
    '''
    requests.delete(f"{url}/clear")

    # Need to create 2 users as the user who creates the channel is assumed to already be in the channel
    # User_1 invites user_2 to join user_1's channel
    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_2['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_server_detail.status_code == 200
    
    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['u_id'] == payload_user_1['u_id']
    assert payload_detail['all_members'][1]['u_id'] == payload_user_2['u_id']
    
    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']

def test_channel_invite_private(url):
    '''
    Testing if channel_invite works on server when channel is private.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com',
        'password': 'testpassword1',
        'name_first': 'Firstname1',
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': False
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_2['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_server_detail.status_code == 200
    
    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['u_id'] == payload_user_1['u_id']
    assert payload_detail['all_members'][1]['u_id'] == payload_user_2['u_id']
    
    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']

def test_channel_invite_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    channels_invite_return = requests.post(f"{url}/channel/invite", json={
        'token': 'invalid_token', 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })
    
    assert channels_invite_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

def test_channel_invite_invalid_channel_id(url):
    '''
    Testing when channel_id is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    channel_invite_return = requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': 'invalid_channel_id', 
        'u_id': payload_user_2['u_id']
    })

    assert channel_invite_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

def test_channel_invite_invalid_u_id(url):
    '''
    Testing when u_id is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    channel_invite_return = requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': 'invalid_u_id'
    })

    assert channel_invite_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

#################################################################################
#                                                                               #
#                      channel_details server testing functions                 #
#                                                                               #
#################################################################################

def test_channel_details_valid(url):
    '''
    Testing if channel_details works on server.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'],
        'u_id': payload_user_2['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'

    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']
    assert payload_listall['channels'][0]['name'] == 'testchannel'

    assert len(payload_detail['owner_members']) == 2
    assert payload_detail['owner_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['owner_members'][1]['name_first'] == 'Firstname2'

def test_channel_details_private(url):
    '''
    Testing if channel_details works on server when channel is private.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': False
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'],
        'u_id': payload_user_1['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'

    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']
    assert payload_listall['channels'][0]['name'] == 'testchannel'

    assert len(payload_detail['owner_members']) == 1
    assert payload_detail['owner_members'][0]['name_first'] == 'Firstname1'

def test_channel_details_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={'invalid_token'}&channel_id={payload_create['channel_id']}")
    
    assert channel_server_detail.status_code == 400

def test_channel_details_invalid_channel_id(url):
    '''
    Testing when channel_id is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={1232312}")
    
    assert channel_server_detail.status_code == 400

def test_channel_details_invalid_name(url):
    '''
    Testing when channel name is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel'*1000, 
        'is_public': True
    })

    assert channels_create_return.status_code == 400

#################################################################################
#                                                                               #
#                      channel_leave server testing functions                   #
#                                                                               #
#################################################################################

def test_channel_leave_valid(url):
    '''
    Testing if channel_leave works on server.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_leave_return = requests.post(f"{url}/channel/leave", json={
        'token': payload_user_2['token'],
        'channel_id': payload_create['channel_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_leave_return.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']

def test_channel_leave_private(url):
    '''
    Testing if channel_leave works on server when channel is private.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': False
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_leave_return = requests.post(f"{url}/channel/leave", json={
        'token': payload_user_2['token'],
        'channel_id': payload_create['channel_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_leave_return.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']    

def test_channel_leave_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_leave_return = requests.post(f"{url}/channel/leave", json={
        'token': 'invalid_token',
        'channel_id': payload_create['channel_id']
    })

    assert channel_leave_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'

def test_channel_leave_invalid_channel_id(url):
    '''
    Testing when channel_id is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_leave_return = requests.post(f"{url}/channel/leave", json={
        'token': payload_user_2['token'],
        'channel_id': 1232112
    })

    assert channel_leave_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200
    
    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'

def test_channel_leave_already_left(url):
    '''
    Testing when the user tries to leave a channel they are not in.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    channel_leave_return = requests.post(f"{url}/channel/leave", json={
        'token': payload_user_2['token'],
        'channel_id': payload_create['channel_id']
    })

    assert channel_leave_return.status_code == 400

#################################################################################
#                                                                               #
#                      channel_join server testing functions                    #
#                                                                               #
#################################################################################

def test_channel_join_valid(url):
    '''
    Testing if channel_join works on server.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()
    auth_register_3 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail3@gmail.com', 
        'password': 'testpassword3', 
        'name_first': 'Firstname3', 
        'name_last': 'Lastname3'
    })
    payload_user_3 = auth_register_3.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_join_return = requests.post(f"{url}/channel/join", json={
        'token': payload_user_3['token'],
        'channel_id': payload_create['channel_id']
    })

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    channels_listall_return = requests.get(f"{url}/channels/listall?token={payload_user_1['token']}")
    payload_listall = channels_listall_return.json()

    assert channel_join_return.status_code == 200

    assert len(payload_detail['all_members']) == 3
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'
    assert payload_detail['all_members'][2]['name_first'] == 'Firstname3'

    assert len(payload_listall['channels']) == 1
    assert payload_listall['channels'][0]['channel_id'] == payload_create['channel_id']

def test_channel_join_private(url):
    '''
    Testing if channel_join works on server when channel is private.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()
    auth_register_3 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail3@gmail.com', 
        'password': 'testpassword3', 
        'name_first': 'Firstname3', 
        'name_last': 'Lastname3'
    })
    payload_user_3 = auth_register_3.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': False
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    channel_join_return = requests.post(f"{url}/channel/join", json={
        'token': payload_user_3['token'],
        'channel_id': payload_create['channel_id']
    })

    assert channel_join_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 2
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'

def test_channel_join_invalid_token(url): 
    '''
    Testing when token is invalid.
    '''  
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    channel_join_return = requests.post(f"{url}/channel/join", json={
        'token': 'invalid_token',
        'channel_id': payload_create['channel_id']
    })
    
    assert channel_join_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

def test_channel_join_invalid_channel_id(url):
    '''
    Testing for when channel_id is invalid.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    channel_join_return = requests.post(f"{url}/channel/join", json={
        'token': payload_user_2['token'],
        'channel_id': 1232112
    })

    assert channel_join_return.status_code == 400

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 1
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'

def test_channel_join_already_in(url):
    '''
    Testing for when the user tries to join a channel they are already in.
    '''
    requests.delete(f"{url}/clear")

    auth_register_1 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })
    payload_user_1 = auth_register_1.json()
    auth_register_2 = requests.post(f"{url}/auth/register", json={
        'email': 'testemail2@gmail.com', 
        'password': 'testpassword2', 
        'name_first': 'Firstname2', 
        'name_last': 'Lastname2'
    })
    payload_user_2 = auth_register_2.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user_1['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_create = channels_create_return.json()

    requests.post(f"{url}/channel/invite", json={
        'token': payload_user_1['token'], 
        'channel_id': payload_create['channel_id'], 
        'u_id': payload_user_2['u_id']
    })

    requests.post(f"{url}/channel/join", json={
        'token': payload_user_2['token'],
        'channel_id': payload_create['channel_id']
    })
    

    channel_server_detail = requests.get(f"{url}/channel/details?token={payload_user_1['token']}&channel_id={payload_create['channel_id']}")
    payload_detail = channel_server_detail.json()

    assert channel_server_detail.status_code == 200

    assert len(payload_detail['all_members']) == 3
    assert payload_detail['all_members'][0]['name_first'] == 'Firstname1'
    assert payload_detail['all_members'][1]['name_first'] == 'Firstname2'

#################################################################################
#                                                                               #
#                  channel_addowner server testing functions                    #
#                                                                               #
#################################################################################

def test_channel_addowner(url):
    '''
    Testing if addowner works.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })

    requests.post(f"{url}/channel/addowner", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })
    
    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 2
    assert payload4['owner_members'][0]['u_id'] == payload1['u_id']
    assert payload4['owner_members'][0]['name_first'] == 'sand'
    assert payload4['owner_members'][0]['name_last'] == 'sou'
    assert payload4['owner_members'][1]['u_id'] == payload2['u_id']
    assert payload4['owner_members'][1]['name_first'] == 'sandy'
    assert payload4['owner_members'][1]['name_last'] == 'souy'

def test_channel_addowner_invalid_token(url):
    '''
    Testing for invalid token.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    channel_addowner = requests.post(f"{url}/channel/addowner", json={
        'token': 'invalid_token', 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })
    
    assert channel_addowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 1

def test_channel_addowner_invalid_channel_id(url):
    '''
    Testing for invalid channel id.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    channel_addowner = requests.post(f"{url}/channel/addowner", json={
        'token': payload1['token'], 
        'channel_id': '12321321', 
        'u_id': payload2['u_id']
    })
    
    assert channel_addowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 1

def test_channel_addowner_unauthorised(url):
    '''
    Testing for unauthorised user.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    channel_addowner = requests.post(f"{url}/channel/addowner", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })
    
    assert channel_addowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 1

def test_channel_addowner_already_owner(url):
    '''
    Testing if user is already owner.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    channel_addowner = requests.post(f"{url}/channel/addowner", json={
        'token': payload1['token'], 
        'channel_id': payload2['channel_id'], 
        'u_id': payload1['u_id']
    })
    
    assert channel_addowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload2['channel_id']}"))
    payload3 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload3['owner_members']) == 1

#################################################################################
#                                                                               #
#               channel_removeowner server testing functions                    #
#                                                                               #
#################################################################################

def test_channel_removeowner(url):
    '''
    Testing if remove owner works.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    requests.post(f"{url}/channel/addowner", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })
    requests.post(f"{url}/channel/removeowner", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload1['u_id']
    })

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 1
    assert payload4['owner_members'][0]['u_id'] == payload2['u_id']
    assert payload4['owner_members'][0]['name_first'] == 'sandy'
    assert payload4['owner_members'][0]['name_last'] == 'souy'

def test_channel_removeowner_invalid_token(url):
    '''
    Testing for invalid token.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    requests.post(f"{url}/channel/addowner", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })
    channel_removeowner = requests.post(f"{url}/channel/removeowner", json={
        'token': 'invalid_token', 
        'channel_id': payload3['channel_id'], 
        'u_id': payload1['u_id']
    })

    assert channel_removeowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 2

def test_channel_removeowner_invalid_channel_id(url):
    '''
    Testing for invalid channel id.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    requests.post(f"{url}/channel/addowner", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })
    channel_removeowner = requests.post(f"{url}/channel/removeowner", json={
        'token': 'invalid_token', 
        'channel_id': '12323213', 
        'u_id': payload1['u_id']
    })

    assert channel_removeowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 2

def test_channel_removeowner_not_owner(url):
    '''
    Testing if user is not owner.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    channel_removeowner = requests.post(f"{url}/channel/removeowner", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload2['u_id']
    })

    assert channel_removeowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 1

def test_channel_removeowner_unauthorised(url):
    '''
    Testing if user is unauthorised.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()
    
    requests.post(f"{url}/channel/join", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id']
    })
    channel_removeowner = requests.post(f"{url}/channel/removeowner", json={
        'token': payload2['token'], 
        'channel_id': payload3['channel_id'], 
        'u_id': payload1['u_id']
    })

    assert channel_removeowner.status_code == 400

    channel_details = requests.get((f"{url}/channel/details?token={payload1['token']}&channel_id={payload3['channel_id']}"))
    payload4 = channel_details.json()

    assert channel_details.status_code == 200 
    assert len(payload4['owner_members']) == 1

#################################################################################
#                                                                               #
#                   channel_messages server testing functions                   #
#                                                                               #
#################################################################################

def test_channel_messages(url):
    '''
    Testing if messages works.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'message': 'hello'
    })
    requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'message': 'hi'
    })

    channel_messages = requests.get((f"{url}/channel/messages?token={payload1['token']}&channel_id={payload3['channel_id']}&start={0}"))
    payload4 = channel_messages.json()
    
    assert payload4['messages'][0].get('message') == 'hi'

def test_channel_messages_invalid_channel_id(url):
    '''
    Testing for invalid channel id.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'message': 'hello'
    })

    channel_messages = requests.get((f"{url}/channel/messages?token={payload1['token']}&channel_id={123213}&start={0}"))
    assert channel_messages.status_code == 400

def test_channel_messages_greater_start(url):
    '''
    Testing if start is out of range.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'message': 'hello'
    })

    channel_messages = requests.get((f"{url}/channel/messages?token={payload1['token']}&channel_id={payload3['channel_id']}&start={1}"))
    assert channel_messages.status_code == 400

def test_channel_messages_unauthorised(url):
    '''
    Testing if user is unauthorised.
    '''
    requests.delete(f"{url}/clear")

    auth_reg1 = requests.post(f"{url}/auth/register", json={
        'email': 'sand@gmail.com', 
        'password': 'password', 
        'name_first': 'sand', 
        'name_last': 'sou'
    })
    payload1 = auth_reg1.json()
    auth_reg2 = requests.post(f"{url}/auth/register", json={
        'email': 'sandy@gmail.com', 
        'password': 'password', 
        'name_first': 'sandy', 
        'name_last': 'souy'
    })
    payload2 = auth_reg2.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'chan', 
        'is_public': True
    })
    payload3 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload3['channel_id'], 
        'message': 'hello'
    })

    channel_messages = requests.get((f"{url}/channel/messages?token={payload2['token']}&channel_id={payload3['channel_id']}&start={0}"))
    assert channel_messages.status_code == 400
