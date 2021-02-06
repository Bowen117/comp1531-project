'''
Imported files for message_test.
'''
import datetime
import threading
import pytest
from error import InputError, AccessError
from channels import channels_create
from channel import channel_join
from auth import auth_register
from other import clear, search
from message import message_send, message_remove, message_edit, message_sendlater, message_react, message_unreact, message_pin, message_unpin

#################################################################################
#                                                                               #
#                      message_edit testing functions                           #
#                                                                               #
#################################################################################

def test_invalid_token():
    '''
    Testing for an invalid token.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_edit('invlaid_token', message_info.get('message_id'), 'Hello World!!!')

def test_invalid_message_id():
    '''
    Testing for an invallid message_id.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(InputError):
        message_edit(user_1.get('token'), 'invalid_message_id', 'Hello World!!!')

def test_edit_message_not_from_person_or_owner():
    '''
    Testing if the corresponding message_id belongs to the user.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    user_2 = auth_register("test_emil2@gamil.com", "password", "User_2", "User_last_2")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_edit(user_2.get('token'), message_info.get('message_id'), 'Hello World!!!')

def test_message_too_long():
    '''
    Testing if the edited message is too long.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(InputError):
        message_edit(user_1.get('token'), message_info.get('message_id'), 'a'*10001)

def test_no_edit_message():
    '''
    Testing if there is no edited message.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    message_edit(user_1.get('token'), message_info.get('message_id'), '')

    message_search = search(user_1['token'], '')
    assert message_search['messages'][0].get('message_id') == message_info.get('message_id')
    assert message_search['messages'][0].get('u_id') == user_1['u_id']
    assert message_search['messages'][0].get('message') == ''

def test_valid_message_edit():
    '''
    Testing for a valid message edited.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    message_edit(user_1.get('token'), message_info.get('message_id'), 'Hellooo Worlldddd!!!!')
    message_search = search(user_1['token'], 'Hellooo Worlldddd!!!!')

    assert message_search['messages'][0].get('message_id') == message_info.get('message_id')
    assert message_search['messages'][0].get('u_id') == user_1['u_id']
    assert message_search['messages'][0].get('message') == 'Hellooo Worlldddd!!!!'

def test_msg_not_from_user():
    '''
    Testing for a valid message edited by a channel owner.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    user_2 = auth_register("test_email2@gmail.com", "password", "User_2", "User_last_2")
    auth_register("test_email3@gmail.com", "password", "User_3", "User_last_3")

    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    channel_join(user_2.get('token'), channel_1.get('channel_id'))
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_edit(user_2.get('token'), message_info.get('message_id'), 'Hellooo Worlldddd!!!!')

def test_owner_edit_access():
    '''
    Testing for a valid message edited by a channel owner.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    user_2 = auth_register("test_email2@gmail.com", "password", "User_2", "User_last_2")
    auth_register("test_email3@gmail.com", "password", "User_3", "User_last_3")

    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    channel_join(user_2.get('token'), channel_1.get('channel_id'))
    message_info = message_send(user_2.get('token'), channel_1.get('channel_id'), 'Hello world')

    print(message_info)
    message_edit(user_2.get('token'), message_info.get('message_id'), 'Hellooo Worlldddd!!!!')
    message_search = search(user_1['token'], 'Hellooo Worlldddd!!!!')

    assert message_search['messages'][0].get('message_id') == message_info.get('message_id')
    assert message_search['messages'][0].get('u_id') == user_2['u_id']
    assert message_search['messages'][0].get('message') == 'Hellooo Worlldddd!!!!'

def test_flocker_owner_access():
    '''
    Testing for a valid message edited by a flockr owner.
    '''
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    print(message_info)
    message_edit(user_1.get('token'), message_info.get('message_id'), 'Hellooo Worlldddd!!!!')
    message_search = search(user_1['token'], 'Hellooo Worlldddd!!!!')

    assert message_search['messages'][0].get('message_id') == message_info.get('message_id')
    assert message_search['messages'][0].get('u_id') == user_1['u_id']
    assert message_search['messages'][0].get('message') == 'Hellooo Worlldddd!!!!'

def test_message_edit_emty_string():
    '''
    Testing if the message is deleted when an empty string is given to message_edit.
    '''
    user_info = auth_register("test_user1@gamil.com", "password", "User_1", "Last_1")

    channel_info = channels_create(user_info['token'], 'test_one', True)

    msg_info = message_send(user_info['token'], channel_info['channel_id'], "Test msg!")

    message_edit(user_info['token'], msg_info['message_id'], '')
    assert search(user_info['token'], 'a'*99) == {"messages": []}

#################################################################################
#                                                                               #
#                      message_send testing functions                           #
#                                                                               #
#################################################################################

def test_inputerror_message_too_long():
    '''
    Error is raised if the message is greater than 1000 words.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')
    channel = channels_create(user_1_token, "channel1", True)
    channel1_id = channel.get("channel_id")
    message_to_send = "a"*1001
    with pytest.raises(InputError):
        message_send(user_1_token, channel1_id, message_to_send)

def test_invalid_channel_id():
    '''
    Error is raised if an invalid channel id is presented.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')
    auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    channels_create(user_1_token, "channel1", True)
    with pytest.raises(AccessError):
        message_send(user_1_token, 'invalid_token', "I really should delete genshin")

def test_user_not_from_channel():
    '''
    Error is raised if the user is not from the current channel.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')
    user_2 = auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_token = user_2.get('token')
    channel = channels_create(user_1_token, "channel1", True)
    channel1_id = channel.get("channel_id")
    with pytest.raises(AccessError):
        message_send(user_2_token, channel1_id, "I really should delete genshin")

def test_message_sent_invalid_token():
    '''
    Error is raised if the token is invalid.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')
    channel = channels_create(user_1_token, "channel1", True)
    channel1_id = channel.get("channel_id")
    auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    with pytest.raises(AccessError):
        message_send("invalid_token", channel1_id, "I really should delete genshin")

def test_message_ids():
    '''
    Test for a valid message send.
    '''
    clear()
    user_1 = auth_register("user1@gamil.com", "password", "User_1", "Last_1")
    channel1 = channels_create(user_1['token'], 'test_one', True)

    message_id = message_send(user_1['token'], channel1['channel_id'], 'a')
    # To test that message actually exists.

    message_search = search(user_1['token'], 'a')

    assert message_search['messages'][0].get('message_id') == message_id.get('message_id')
    assert message_search['messages'][0].get('u_id') == user_1['u_id']
    assert message_search['messages'][0].get('message') == 'a'



#################################################################################
#                                                                               #
#                      message_remove testing functions                         #
#                                                                               #
#################################################################################

def test_remove_invalid_token():
    '''
    Testing for an invalid token.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_remove('invalid_token', message_info.get('message_id'))

def test_remove_invalid_message_id():
    '''
    Testing for an invalid message ID.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(InputError):
        message_remove(user_1.get('token'), 'invalid_message_id')

def test_remove_message_non_existing():
    '''
    Testing for a message that has already been removed.
    '''
    clear()
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")

    with pytest.raises(InputError):
        message_remove(user_1.get('token'), 'message_id')

def test_remove_request_made_by_invalid_user():
    '''
    Testing for the validity of the user requesting for message to be removed.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    user_2 = auth_register("email2@gmail.com", "password", "First_2", "Last_2")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_remove(user_2.get('token'), message_info.get('message_id'))

def test_remove_valid_message_remove():
    '''
    Testing for a valid message removed.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_remove(user_1.get('token'), message_info.get('message_id'))
    message_search = search(user_1.get('token'), 'Hello world')
    print(message_search)
    assert message_search == {'messages': []}

def test_remove_msg_notfromtokens():
    '''
    Testing for a valid message removed by a flockr owner.
    '''
    clear()
    user = auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user.get('token'), 'channel_1', True)
    channel_join(user_1.get('token'), channel_1.get('channel_id'))
    message_info = message_send(user.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_remove(user_1.get('token'), message_info.get('message_id'))
   

def test_remove_flocker_owner_access():
    '''
    Testing for a valid message removed by a flockr owner.
    '''
    clear()
    user = auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    channel_join(user.get('token'), channel_1.get('channel_id'))
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    print(message_info)
    message_remove(user_1.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search == {'messages': []}

#################################################################################
#                                                                               #
#                      message_sendlater testing functions                      #
#                                                                               #
#################################################################################

def test_sendlater_invalid_token():
    '''
    Testing for an error if the token id is invalid.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    
    time_sent = time.timestamp()

    with pytest.raises(AccessError):
        message_sendlater("invalid_token", channel_1.get('channel_id'), 'Hello world', time_sent)
        
def test_sendlater_invalid_channel_id():
    '''
    Testing for an error if the channel id is invalid.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channels_create(user_1.get('token'), 'channel_1', True)
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    
    time_sent = time.timestamp()

    with pytest.raises(InputError):
        message_sendlater(user_1["token"], 123412341, 'Hello world', time_sent)

def test_message_send_later_too_long():
    '''
    Testing for an error if the message is too long.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    
    time_sent = time.timestamp()

    with pytest.raises(InputError):
        message_sendlater(user_1["token"], channel_1.get('channel_id'), 'w'*100000, time_sent)

def test_message_send_later_no_message():
    '''
    Testing if the user didnt send a message.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    
    time_sent = time.timestamp()

    with pytest.raises(InputError):
        message_sendlater(user_1["token"], channel_1.get('channel_id'), '', time_sent)

def test_sendlater_user_not_in_channel():
    '''
    Testing for an error if the user is not in the channel.
    '''
    clear()
    user = auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user.get('token'), 'channel_1', True)
    
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    time_sent = time.timestamp()

    with pytest.raises(AccessError):
        message_sendlater(user_1["token"], channel_1.get('channel_id'), 'w', time_sent)

def test_time_sent_in_the_past():
    '''
    Testing for the an error when the useer send a message to the past
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    
    time = datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(0, 5)
    
    time_sent = time.timestamp()

    with pytest.raises(InputError):
        message_sendlater(user_1["token"], channel_1.get('channel_id'), 'w', time_sent)



def test_messge_send_later_valid():
    '''
    Testing for message sent later.
    '''
    clear()
    auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    
    time = datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(0, 5)
    
    time_sent = time.timestamp()
    
    print(time_sent)

    def test_sent_later_check(token, message): 
        messages = search(token, message)
        assert messages == {'messages': []}

    timer = threading.Timer(3, test_sent_later_check, args=(user_1['token'], 'Hello world')) 
    timer.start() 
    
    

    message_id = message_sendlater(user_1["token"], channel_1.get('channel_id'), 'Hello world', time_sent)
    messages_search = search(user_1['token'], 'Hello world')
    print(messages_search)
    assert messages_search['messages'][0]['message_id'] == message_id['message_id']
    assert messages_search['messages'][0]['time_created'] == time_sent

#################################################################################
#                                                                               #
#                      message_react testing functions                          #
#                                                                               #
#################################################################################

def test_react_invalid_token():
    '''
    Testing for invalid token.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(AccessError):
        message_react('invalid_token', message_info.get('message_id'), 1)

def test_react_invalid_message_id():
    '''
    Testing for invalid message ID.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(InputError):
        message_react(user_1['token'], 'invalid_message_id', 1)

def test_react_invalid_react_id():
    '''
    Testing for invalid react ID.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(InputError):
        message_react(user_1['token'], message_info.get('message_id'), 123123123)

def test_react_already_reacted():
    '''
    Testing when the message has already been reacted by the authorised user.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_react(user_1['token'], message_info.get('message_id'), 1)

    with pytest.raises(InputError):
        message_react(user_1['token'], message_info.get('message_id'), 1)

def test_react_valid():
    '''
    Testing if message_react works.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    message_react(user_1['token'], message_info.get('message_id'), 1)
    message_search = search(user_1['token'], 'Hello world')

    assert message_search['messages'][0]['reacts'] == [{
        'react_id': 1,
        'u_ids': [user_1.get('u_id')],
        'is_this_user_reacted': True,
    }]

 #################################################################################
#                                                                               #
#                      message_unreact testing functions                        #
#                                                                               #
#################################################################################   

def test_unreact_invalid_token():
    '''
    Testing for invalid token.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_react(user_1.get('token'), message_info.get('message_id'), 1)

    with pytest.raises(AccessError):
        message_unreact('invalid_token', message_info.get('message_id'), 1)

def test_unreact_invalid_message_id():
    '''
    Testing for invalid message ID.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_react(user_1.get('token'), message_info.get('message_id'), 1)

    with pytest.raises(InputError):
        message_unreact(user_1['token'], 'invalid_message_id', 1)

def test_unreact_invalid_react_id():
    '''
    Testing for invalid react ID.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_react(user_1.get('token'), message_info.get('message_id'), 1)

    with pytest.raises(InputError):
        message_unreact(user_1['token'], message_info.get('message_id'), 123123123)

def test_unreact_no_react():
    '''
    Testing when user tries to unreact a message that does not have a react.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    with pytest.raises(InputError):
        message_unreact(user_1['token'], message_info.get('message_id'), 1)

def test_unreact_already_unreacted():
    '''
    Testing when the user tries to unreact a message they have already unreacted.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_react(user_1.get('token'), message_info.get('message_id'), 1)
    message_unreact(user_1.get('token'), message_info.get('message_id'), 1)
    
    with pytest.raises(InputError):
        message_unreact(user_1['token'], message_info.get('message_id'), 1)

def test_unreact_valid():
    '''
    Testing if message_unreact works.
    '''
    clear()
    auth_register('email@gmail.com', 'password', 'First', 'Last')
    user_1 = auth_register('email1@gmail.com', 'password', 'First_1', 'Last_1')
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_react(user_1.get('token'), message_info.get('message_id'), 1)

    message_unreact(user_1['token'], message_info.get('message_id'), 1)
    message_search = search(user_1['token'], 'Hello world')

    assert message_search['messages'][0]['reacts'] == [{
        'react_id': 1,
        'u_ids': [],
        'is_this_user_reacted': False,
    }]

#################################################################################
#                                                                               #
#                      message_pin testing functions                            #
#                                                                               #
#################################################################################
    
def test_pin_invalid_msg_id():   
    '''
    Testing for an invalid message ID.
    '''
    clear()
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    with pytest.raises(InputError):
        message_pin(user_1.get('token'), 'invalid_id')

def test_pin_not_in_channel():
    clear()
    user_0 = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_0.get('token'), 'channel_1', True)
    message_info = message_send(user_0.get('token'), channel_1.get('channel_id'), 'Hello world')
    with pytest.raises(AccessError):
        message_pin(user_1.get('token'), message_info.get('message_id'))

def test_message_already_pinned():
    clear()
    user_0 = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    channel_1 = channels_create(user_0.get('token'), 'channel_1', True)
    message_info = message_send(user_0.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_pin(user_0.get('token'), message_info.get('message_id'))
    with pytest.raises(InputError):
        message_pin(user_0.get('token'), message_info.get('message_id'))
    
    
def test_owner_pin_from_outside_channel():
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")   
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == False   
    
    message_pin(user_1.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == True
    
def test_valid_pin_from_inside_channel():
    clear()
    user_0 = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")   
    channel_1 = channels_create(user_0.get('token'), 'channel_1', True)
    channel_join(user_1.get('token'), channel_1.get('channel_id'))
    
    message_info = message_send(user_0.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == False   
    
    
    message_pin(user_0.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == True   
   
#################################################################################
#                                                                               #
#                      message_unpin testing functions                          #
#                                                                               #
#################################################################################
    
def test_unpin_invalid_msg_id():   
    '''
    Testing for an invalid message ID.
    '''
    clear()
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_pin(user_1.get('token'), message_info.get('message_id'))
    with pytest.raises(InputError):
        message_unpin(user_1.get('token'), 'invalid_id')

def test_unpin_not_in_channel():
    clear()
    user_0 = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user_0.get('token'), 'channel_1', True)
    message_info = message_send(user_0.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_pin(user_0.get('token'), message_info.get('message_id'))
    with pytest.raises(AccessError):
        message_unpin(user_1.get('token'), message_info.get('message_id'))

def test_message_already_unpinned():
    clear()
    user_0 = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    channel_1 = channels_create(user_0.get('token'), 'channel_1', True)
    message_info = message_send(user_0.get('token'), channel_1.get('channel_id'), 'Hello world')
    with pytest.raises(InputError):
        message_unpin(user_0.get('token'), message_info.get('message_id'))
    
    
def test_owner_unpin_from_outside_channel():
    clear()
    auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")   
    channel_1 = channels_create(user_1.get('token'), 'channel_1', True)
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == False   
    
    message_pin(user_1.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == True
    
    message_unpin(user_1.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == False
    
def test_valid_unpin_from_inside_channel():
    clear()
    user_0 = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")   
    channel_1 = channels_create(user_0.get('token'), 'channel_1', True)
    channel_join(user_1.get('token'), channel_1.get('channel_id'))
    
    message_info = message_send(user_0.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == False   
    
    message_pin(user_0.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == True   
   
    message_unpin(user_0.get('token'), message_info.get('message_id'))
    message_search = search(user_1['token'], 'Hello world')
    assert message_search['messages'][0].get('message') == 'Hello world'
    assert message_search['messages'][0].get('is_pinned') == False
    
