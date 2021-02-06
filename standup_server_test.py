'''
Imported files for standup_server_test.
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
#                      standup_start server testing functions                   #
#                                                                               #
#################################################################################

def test_standup_server_token_invalid(url):
    '''
    Testing error for invalid token
    '''

    requests.delete(f"{url}/clear")
    auth_register = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })

    payload_user = auth_register.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_channel = channels_create_return.json()

    return_standup = requests.post(f"{url}/standup/start", json={
        'token': 'invalid',
        'channel_id': payload_channel['channel_id'],
        'length': 5
    })

    assert return_standup.status_code == 400

def test_standup_server_channel_invalid(url):
    '''
    Testing error for invalid channel
    '''

    requests.delete(f"{url}/clear")
    auth_register = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })

    payload_user = auth_register.json()

    requests.post(f"{url}/channels/create", json={
        'token': payload_user['token'], 
        'name': 'testchannel', 
        'is_public': True
    })

    return_standup = requests.post(f"{url}/standup/start", json={
        'token': payload_user['token'],
        'channel_id': 10,
        'length': 5
    })

    assert return_standup.status_code == 400

def test_working_start(url):
    '''
    Testing error for invalid channel
    '''

    requests.delete(f"{url}/clear")
    auth_register = requests.post(f"{url}/auth/register", json={
        'email': 'testemail1@gmail.com', 
        'password': 'testpassword1', 
        'name_first': 'Firstname1', 
        'name_last': 'Lastname1'
    })

    payload_user = auth_register.json()

    channels_create_return = requests.post(f"{url}/channels/create", json={
        'token': payload_user['token'], 
        'name': 'testchannel', 
        'is_public': True
    })
    payload_channel = channels_create_return.json()

    requests.post(f"{url}/standup/start", json={
        'token': payload_user['token'],
        'channel_id': payload_channel['channel_id'],
        'length': 5
    })

    requests.post(f"{url}/standup/send", json={ 
        'token': payload_user['token'],
        'channel_id': payload_channel['channel_id'],
        'message': "Msg1"
    })

    sleep(5)

    return_message = requests.get(f"{url}/channel/messages?token={payload_user['token']}&channel_id={payload_channel['channel_id']}&start={'0'}")
    payload_message = return_message.json()
    print(payload_message)
    assert payload_message.get('messages')[0].get('message') == "firstname1lastname1: Msg1"
