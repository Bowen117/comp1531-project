import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import json
import requests


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


def test_hangman_token_error(url):
  
    requests.delete(f"{url}/clear")
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    chan = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = chan.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    payload = requests.post(f"{url}/message/send", json={
        'token': 'token', 
        'channel_id': payload2['channel_id'], 
        'message': "/guess B"
    })


    assert payload.status_code == 400


def test_hangman_channel_error(url):
    requests.delete(f"{url}/clear")
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    chan = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = chan.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    payload3 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })
 
    assert payload3.status_code == 400

def test_hangman_same_error(url):

    requests.delete(f"{url}/clear")
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    chan = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = chan.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    payload = requests.post(f"{url}/message/send", json={
        'token': 'token', 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    assert payload.status_code == 400


def test_working_hang(url):
    requests.delete(f"{url}/clear")
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    chan = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = chan.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    payload3 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/guess a"
    })

    assert payload3.status_code == 200

    payload4 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/stop"
    })

    assert payload4.status_code == 200

def test_working_hang2(url):
    requests.delete(f"{url}/clear")
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    chan = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = chan.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    payload3 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/guess a"
    })

    assert payload3.status_code == 200

    payload4 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/stop"
    })

    assert payload4.status_code == 200

def test_working_hang3(url):
    requests.delete(f"{url}/clear")
    auth_reg = requests.post(f"{url}/auth/register", json={
        'email': 'ando@gmail.com', 
        'password': 'password', 
        'name_first': 'ando', 
        'name_last': 'pech'
    })

    payload = auth_reg.json()
    chan = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'aaaaa', 
        'is_public': True
    })
    payload2 = chan.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/hangman"
    })

    payload3 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/guess a"
    })

    assert payload3.status_code == 200

    payload4 = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "/stop"
    })

    assert payload4.status_code == 200
