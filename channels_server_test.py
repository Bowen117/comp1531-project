'''
Imported files for channels_server_test.
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
#                      channels_create server testing functions                 #
#                                                                               #
#################################################################################

def test_channels_create(url):
    '''
    Testing if channels_create works on server.
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
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    list_channel = requests.get(f"{url}/channels/listall?token={payload['token']}")
    payload3 = list_channel.json()
    
    assert list_channel.status_code == 200
    assert len(payload3['channels']) == 1
    assert payload3['channels'][0]['channel_id'] == payload2['channel_id']
    assert payload3['channels'][0]['name'] == "aaaaa"

def test_channels_create_private(url):
    '''
    Testing if channels_create works on server when the channel is private.
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
        'name': 'aaaaa', 
        'is_public': False
    })
    payload2 = channel_create.json()
    
    list_channel = requests.get(f"{url}/channels/listall?token={payload['token']}")
    payload3 = list_channel.json()
    
    assert list_channel.status_code == 200
    assert len(payload3['channels']) == 1
    assert payload3['channels'][0]['channel_id'] == payload2['channel_id']
    assert payload3['channels'][0]['name'] == "aaaaa"

def test_channels_create_invalid_token(url):
    '''
    Testing when the token is invalid.
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
        'token': 'invalid_token', 
        'name': 'aaaaa', 
        'is_public': True
    })
    
    assert channel_create.status_code == 400

    list_channel = requests.get(f"{url}/channels/listall?token={payload['token']}")
    payload3 = list_channel.json()
    
    assert list_channel.status_code == 200
    assert len(payload3['channels']) == 0

def test_channels_create_invalid_name(url):
    '''
    Testing when the channel name is invalid.
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
        'name': 'a'*20000, 
        'is_public': True
    })
    
    assert channel_create.status_code == 400

    list_channel = requests.get(f"{url}/channels/listall?token={payload['token']}")
    payload3 = list_channel.json()
    
    assert list_channel.status_code == 200
    assert len(payload3['channels']) == 0

#################################################################################
#                                                                               #
#                      channels_list server testing functions                   #
#                                                                               #
#################################################################################
def test_channels_list(url):
    '''
    Testing if channels_list works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    
    auth_reg0 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload0 = auth_reg0.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = channel_create.json()
    channel_create2 = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'bbbbb', 
        'is_public': True
    })
    payload3 = channel_create2.json()
    requests.post(f"{url}/channels/create", json={'token': payload0['token'], 
    'name': 'ccccc', 
    'is_public': True
    })
    
    list_channel = requests.get(f"{url}/channels/list?token={payload['token']}")
    payload5 = list_channel.json()
    
    assert list_channel.status_code == 200
    assert len(payload5['channels']) == 2
    assert payload5['channels'][0]['channel_id'] == payload2['channel_id']
    assert payload5['channels'][0]['name'] == "aaaaa"
    assert payload5['channels'][1]['channel_id'] == payload3['channel_id']
    assert payload5['channels'][1]['name'] == "bbbbb"

def test_channels_list_invalid_token(url):
    '''
    Testing when the token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    
    auth_reg0 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload0 = auth_reg0.json()

    requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    
    requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'bbbbb', 
        'is_public': True
    })
    requests.post(f"{url}/channels/create", json={
        'token': payload0['token'], 
        'name': 'ccccc', 
        'is_public': True
    })
    
    list_channel = requests.get(f"{url}/channels/list?token={'invalid_token'}")
    
    assert list_channel.status_code == 400

#################################################################################
#                                                                               #
#                      channels_listall server testing functions                #
#                                                                               #
#################################################################################  

def test_channels_listall(url):
    '''
    Testing if channels_listall works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload = auth_reg.json()
    
    auth_reg0 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload0 = auth_reg0.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = channel_create.json()
    channel_create2 = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'bbbbb', 
        'is_public': True
    })
    payload3 = channel_create2.json()
    channel_create3 = requests.post(f"{url}/channels/create", json={
        'token': payload0['token'], 
        'name': 'ccccc', 
        'is_public': True
    })
    payload4 = channel_create3.json()

    list_channel = requests.get(f"{url}/channels/listall?token={payload['token']}")
    payload5 = list_channel.json()
    
    assert len(payload5['channels']) == 3
    assert payload5['channels'][0]['channel_id'] == payload2['channel_id']
    assert payload5['channels'][0]['name'] == "aaaaa"
    assert payload5['channels'][1]['channel_id'] == payload3['channel_id']
    assert payload5['channels'][1]['name'] == "bbbbb"
    assert payload5['channels'][2]['channel_id'] == payload4['channel_id']
    assert payload5['channels'][2]['name'] == "ccccc"

def test_channels_listall_invalid(url):
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
    
    auth_reg0 = requests.post(f"{url}/auth/register", json={
        'email': 'kiet@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })
    payload0 = auth_reg0.json()

    requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    requests.post(f"{url}/channels/create", json={
        'token': payload['token'],
        'name': 'bbbbb', 
        'is_public': True
    })
    requests.post(f"{url}/channels/create", json={
        'token': payload0['token'], 
        'name': 'ccccc', 
        'is_public': True
    })

    list_channel = requests.get(f"{url}/channels/listall?token={'invalid_token'}")
    assert list_channel.status_code == 400
