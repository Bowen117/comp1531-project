'''
Imported files for message_server_test.
'''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep

import threading
import requests
import json
import auth
import channels
import channel
import datetime 

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
#                      message_send server testing functions                    #
#                                                                               #
#################################################################################

def test_invalid_message(url):
    '''
    Testing when message is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    raw = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "a"*1500
    })

    assert raw.status_code == 400
    
def test_snd_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    raw = requests.post(f"{url}/message/send", json={
        'token': '420', 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })

    assert raw.status_code == 400
    
def test_snd_invalid_channel_id(url):
    '''
    Testing when channel_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })

    raw = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': "1231", 
        'message': "howdy"
    })

    assert raw.status_code == 400

def test_snd_not_in_channel(url):
    '''
    Testing when trying to send a message in a channel not in.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    raw = requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })

    assert raw.status_code == 400

def test_snd_message_valid(url):
    '''
    Testing if message_send works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
   
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'channelone', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
   
    channel_msg = requests.get(f"{url}/channel/messages?token={payload['token']}&channel_id={payload2['channel_id']}&start={'0'}")
    payload4 = channel_msg.json()
    
    assert payload4['messages'][0].get('message') == "banana"

#################################################################################
#                                                                               #
#                      message_remove testing functions                         #
#                                                                               #
#################################################################################

def test_rmv_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    msg_snd = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    payload3 = msg_snd.json()
    
    raw = requests.delete(f"{url}/message/remove", json={
        'token': '123', 
        'message_id': payload3['message_id']
    })

    assert raw.status_code == 400

def test_rmv_invalid_msg_id(url):
    '''
    Testing when message_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    
    raw = requests.delete(f"{url}/message/remove", json={
        'token': payload['token'], 
        'message_id': '123'
    })

    assert raw.status_code == 400

def test_rmv_not_in_channel(url):
    '''
    Testing when trying to a remove a message in a channel not in.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    msg_snd = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    payload3 = msg_snd.json()
    
    raw = requests.delete(f"{url}/message/remove", json={
        'token': payload1['token'], 
        'message_id': payload3['message_id']
    })

    assert raw.status_code == 400 



#################################################################################
#                                                                               #
#                      message_edit testing functions                           #
#                                                                               #
#################################################################################

def test_edit_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    msg_snd = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    payload3 = msg_snd.json()
    
    raw = requests.put(f"{url}/message/edit", json={
        'token': '123', 
        'message_id': payload3['message_id'], 
        'message': "brownie"
    })

    assert raw.status_code == 400
   
def test_edit_invalid_msg_id(url):
    '''
    Testing when message_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    
    raw = requests.put(f"{url}/message/edit", json={
        'token': payload['token'], 
        'message_id': '123', 
        'message': "brownie"
    })

    assert raw.status_code == 400

def test_edit_too_long_msg(url):
    '''
    Testing when the message is too long.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    msg_snd = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    payload3 = msg_snd.json()
    
    raw = requests.put(f"{url}/message/edit", json={
        'token': payload['token'], 
        'message_id': payload3['message_id'], 
        'message': "a"*1500
    })

    assert raw.status_code == 400
           
def test_edit_not_in_channel(url):
    '''
    Testing when trying to edit a message in a channel not in.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()
    
    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    msg_snd = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    payload3 = msg_snd.json()
    
    raw = requests.put(f"{url}/message/edit", json={
        'token': payload1['token'], 
        'message_id': payload3['message_id'], 
        'message': "brownie"
    })

    assert raw.status_code == 400

def test_edit_msg_valid(url):
    '''
    Testing if message_edit works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    msg_snd = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "howdy"
    })
    payload3 = msg_snd.json()
    
    requests.put(f"{url}/message/edit", json={
        'token': payload['token'], 
        'message_id': payload3['message_id'], 
        'message': "brownie"
    })
    
    channel_msg = requests.get(f"{url}/channel/messages?token={payload['token']}&channel_id={payload2['channel_id']}&start={'0'}")
    payload4 = channel_msg.json()
    
    assert payload4['messages'][0].get('message') == "brownie"


#################################################################################
#                                                                               #
#                      message_sendlater testing functions                      #
#                                                                               #
#################################################################################

def test_sendlater_invalid_token(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    auth_reg_return.json()
    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw  = requests.post(f"{url}/message/sendlater", json={'token': "invalid_token", 'channel_id': payload_2['channel_id'], 'message': 'Hello world', 'time_sent': time_sent})
        
    assert raw.status_code == 400

def test_sendlater_invalid_channel_id(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    auth_reg_return.json()
    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    channel_create.json()
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw  = requests.post(f"{url}/message/sendlater", json={'token': payload_1['token'], 'channel_id': 12341234, 'message': 'Hello world', 'time_sent': time_sent})
        
    assert raw.status_code == 400


def test_message_send_later_too_long(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    auth_reg_return.json()
    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw  = requests.post(f"{url}/message/sendlater", json={'token': payload_1['token'], 'channel_id': payload_2['channel_id'], 'message': 'H'*100000, 'time_sent': time_sent})
        
    assert raw.status_code == 400

def test_message_send_later_no_message(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    auth_reg_return.json()
    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw = raw  = requests.post(f"{url}/message/sendlater", json={'token': payload_1['token'], 'channel_id': payload_2['channel_id'], 'message': '', 'time_sent': time_sent})
        
    assert raw.status_code == 400

def test_sendlater_user_not_in_channel(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    payload = auth_reg_return.json()

    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw = raw  = requests.post(f"{url}/message/sendlater", json={'token': payload_1['token'], 'channel_id': payload_2['channel_id'], 'message': 'Hello_world', 'time_sent': time_sent})
        
    assert raw.status_code == 400

def test_time_sent_in_the_past(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    auth_reg_return.json()
    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()
    
    time = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw  = requests.post(f"{url}/message/sendlater", json={'token': payload_1['token'], 'channel_id': payload_2['channel_id'], 'message': 'H', 'time_sent': time_sent})
        
    assert raw.status_code == 400

def test_messge_send_later_valid(url):
    '''
    Testing for an error if the token id is invalid.
    '''
    requests.delete(f"{url}/clear")
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })

    auth_reg_return.json()
    auth_reg_return_1 = requests.post(f"{url}/auth/register", json={
        'email': 'boop2@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return_1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()
    
    def sent_later_check(): 
        search = requests.get(f"{url}/search?token={payload_1['token']}&query_str={'Hello World'}")
        assert search['messages'] == []

    timer = threading.Timer(4, sent_later_check, args=(payload_1['token'])) 
    timer.start() 

    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    raw = raw  = requests.post(f"{url}/message/sendlater", json={'token': payload_1['token'], 'channel_id': payload_2['channel_id'], 'message': 'Hello World', 'time_sent': time_sent})
    
    search_1 = requests.get(f"{url}/search?token={payload_1['token']}&query_str={'Hello World'}")
    payload6 = search_1.json()
    assert raw.status_code == 200
    assert payload6['messages'][0]['message'] == 'Hello World' 

#################################################################################
#                                                                               #
#                      message_react server testing functions                   #
#                                                                               #
#################################################################################

def test_react_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    raw = requests.post(f"{url}/message/react", json={
        'token': 'invalid_token',
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    assert raw.status_code == 400

def test_react_invalid_message_id(url):
    '''
    Testing when the message_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })

    raw = requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': '123123123',
        'react_id': 1
    })

    assert raw.status_code == 400

def test_react_invalid_react_id(url):
    '''
    Testing when react_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    raw = requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 123123123
    })

    assert raw.status_code == 400

def test_react_already_reacted(url):
    '''
    Testing when user has already reacted the message.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    raw = requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    assert raw.status_code == 400

def test_react_valid(url):
    '''
    Testing if message_react works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    raw = requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    search = requests.get(f"{url}/search?token={payload_1['token']}&query_str={'Hello world'}")
    payload_4 = search.json()

    messages_info = requests.get((f"{url}/channel/messages?token={payload_1['token']}&channel_id={payload_2['channel_id']}&start={0}"))
    payload_5 = messages_info.json()
    print(payload_5)
    assert raw.status_code == 200
    assert payload_4['messages'][0]['reacts'] == [{
        'react_id': 1,
        'u_ids': [payload_5['messages'][0]['u_id']],
        'is_this_user_reacted': True
    }]

#################################################################################
#                                                                               #
#                      message_unreact server testing functions                 #
#                                                                               #
#################################################################################

def test_unreact_invalid_token(url):
    '''
    Testing when token is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    raw = requests.post(f"{url}/message/unreact", json={
        'token': 'invalid_token',
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    assert raw.status_code == 400

def test_unreact_invalid_message_id(url):
    '''
    Testing when message_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    raw = requests.post(f"{url}/message/unreact", json={
        'token': payload_1['token'],
        'message_id': '123123123',
        'react_id': 1
    })

    assert raw.status_code == 400

def test_unreact_invalid_react_id(url):
    '''
    Testing when react_id is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    raw = requests.post(f"{url}/message/unreact", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 123123123
    })

    assert raw.status_code == 400

def test_unreact_already_unreacted(url):
    '''
    Testing when the message has already been unreacted.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    requests.post(f"{url}/message/unreact", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    raw = requests.post(f"{url}/message/unreact", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    assert raw.status_code == 400

def test_unreact_valid(url):
    '''
    Testing if message_unreact works on server.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload_1 = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload_1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload_2 = channel_create.json()

    send_info = requests.post(f"{url}/message/send", json={
        'token': payload_1['token'], 
        'channel_id': payload_2['channel_id'], 
        'message': 'Hello world'
    })
    payload_3 = send_info.json()

    requests.post(f"{url}/message/react", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    raw = requests.post(f"{url}/message/unreact", json={
        'token': payload_1['token'],
        'message_id': payload_3['message_id'],
        'react_id': 1
    })

    search = requests.get(f"{url}/search?token={payload_1['token']}&query_str={'Hello world'}")
    payload_4 = search.json()
    assert raw.status_code == 200
    assert payload_4['messages'][0]['reacts'] == [{
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': False
    }]
    
#################################################################################
#                                                                               #
#                      message_pin server testing functions                     #
#                                                                               #
#################################################################################
def test_pin_invalid_msg_id(url):
    '''
    Testing when message is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    
    raw = requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': '123'
    })

    assert raw.status_code == 400

def test_pin_not_in_channel(url):
    '''
    Testing when not in channel.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()
    
    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    raw = requests.post(f"{url}/message/pin", json={
        'token': payload1['token'],
        'message_id': payload3['message_id']
    })

    assert raw.status_code == 400
            
def test_msg_already_pinned(url):
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    
    raw = requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })

    assert raw.status_code == 400

def test_owner_pin_from_outside_channel(url):
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()
    
    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    search = requests.get(f"{url}/search?token={payload1['token']}&query_str={'banana'}")
    payload4 = search.json()
    
    assert payload4['messages'][0]["is_pinned"] == False

def test_valid_pin_from_inside_channel(url):
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()    

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    
    search = requests.get(f"{url}/search?token={payload['token']}&query_str={'banana'}")
    payload4 = search.json()
    
    assert payload4['messages'][0]["is_pinned"] == True

#################################################################################
#                                                                               #
#                      message_unpin server testing functions                   #
#                                                                               #
#################################################################################
def test_unpin_invalid_msg_id(url):
    '''
    Testing when message is invalid.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    
    raw = requests.post(f"{url}/message/unpin", json={
        'token': payload['token'],
        'message_id': '123'
    })

    assert raw.status_code == 400

def test_unpin_not_in_channel(url):
    '''
    Testing when not in channel.
    '''
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()
    
    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    raw = requests.post(f"{url}/message/unpin", json={
        'token': payload1['token'],
        'message_id': payload3['message_id']
    })
    
    assert raw.status_code == 400
            
def test_msg_already_unpinned(url):
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()

    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()

    raw = requests.post(f"{url}/message/unpin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })

    assert raw.status_code == 400

def test_owner_unpin_from_outside_channel(url):
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()
    
    auth_reg_return1 = requests.post(f"{url}/auth/register", json={
        'email': 'noop@gmail.com', 
        'password': 'password', 
        'name_first': 'noop', 
        'name_last': 'goop'
    })
    payload1 = auth_reg_return1.json()

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload1['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload1['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload1['token'],
        'message_id': payload3['message_id']
    })
    search = requests.get(f"{url}/search?token={payload1['token']}&query_str={'banana'}")
    payload4 = search.json()
    
    assert payload4['messages'][0].get("is_pinned") == True
    
    requests.post(f"{url}/message/unpin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    search2 = requests.get(f"{url}/search?token={payload1['token']}&query_str={'banana'}")
    payload5 = search2.json()
    
    assert payload5['messages'][0].get("is_pinned") == True
   
def test_valid_unpin_from_inside_channel(url):
    requests.delete(f"{url}/clear")
    
    auth_reg_return = requests.post(f"{url}/auth/register", json={
        'email': 'boop@gmail.com', 
        'password': 'password', 
        'name_first': 'boop', 
        'name_last': 'doop'
    })
    payload = auth_reg_return.json()    

    channel_create = requests.post(f"{url}/channels/create", json={
        'token': payload['token'], 
        'name': 'oneechan', 
        'is_public': True
    })
    payload2 = channel_create.json()
    
    info = requests.post(f"{url}/message/send", json={
        'token': payload['token'], 
        'channel_id': payload2['channel_id'], 
        'message': "banana"
    })
    payload3 = info.json()
    
    requests.post(f"{url}/message/pin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    
    search = requests.get(f"{url}/search?token={payload['token']}&query_str={'banana'}")
    payload4 = search.json()
    
    assert payload4['messages'][0].get("is_pinned") == True
    
    requests.post(f"{url}/message/unpin", json={
        'token': payload['token'],
        'message_id': payload3['message_id']
    })
    
    search2 = requests.get(f"{url}/search?token={payload['token']}&query_str={'banana'}")
    payload5 = search2.json()
    
    assert payload5['messages'][0].get("is_pinned") == False    
