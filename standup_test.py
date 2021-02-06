import pytest
import auth
import channels 
import channel 
import standup
import user
import error 
import time
from other import clear 

#####################################################################
#                                                                   #
#                   Standup Start                                   #
#                                                                   #
#####################################################################


def test_standup_tokenwrong():
    '''
    Invalid token
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    with pytest.raises(error.AccessError):
        standup.standup_start("invalid", channel["channel_id"], 10)

    
def test_standup_id_invalid():
    '''
    Invalid channel_id
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    with pytest.raises(error.InputError):
        standup.standup_start(user['token'], "invalid", 2)
    time.sleep(2)

def test_standup_start1():
    """ 
    Tests if standup_start and standup_send works. 
    """
    clear()
    user1 = auth.auth_register("email1@email.com", "password", "Bilbo", "Baggins")
    user2 = auth.auth_register("email2@email.com", "password", "Frodo", "Baggins")
    user3 = auth.auth_register("email3@email.com", "password", "Master", "Sauron")
    channel_dict = channels.channels_create(user1['token'], "test_channel", True)

    channel.channel_join(user2['token'], channel_dict['channel_id'])
    channel.channel_join(user3['token'], channel_dict['channel_id'])

    standup.standup_start(user1['token'], channel_dict['channel_id'], 3)
    standup.standup_send(user1['token'], channel_dict['channel_id'], "message1")
    standup.standup_send(user2['token'], channel_dict['channel_id'], "message2")
    standup.standup_send(user3['token'], channel_dict['channel_id'], "message3")

    time.sleep(5)
    standup.standup_active(user1['token'], channel_dict['channel_id'])

    message_dict = channel.channel_messages(user1['token'], channel_dict['channel_id'], 0)
    assert len(message_dict['messages']) == 1
    assert message_dict['messages'][0]['message'] == ("bilbobaggins: message1\n" +
                                                      "frodobaggins: message2\n" +
                                                      "mastersauron: message3")


def test_standup_start():
    """ 
    Tests if 2 standup_start and standup_send works. 
    """
    clear()
    user1 = auth.auth_register("email1@email.com", "password", "Bilbo", "Baggins")
    user2 = auth.auth_register("email2@email.com", "password", "Frodo", "Baggins")
    user3 = auth.auth_register("email3@email.com", "password", "Master", "Sauron")
    channel_dict = channels.channels_create(user1['token'], "test_channel", True)

    channel.channel_join(user2['token'], channel_dict['channel_id'])
    channel.channel_join(user3['token'], channel_dict['channel_id'])

    standup.standup_start(user1['token'], channel_dict['channel_id'], 3)
    standup.standup_send(user1['token'], channel_dict['channel_id'], "message1")
    standup.standup_send(user2['token'], channel_dict['channel_id'], "message2")
    standup.standup_send(user3['token'], channel_dict['channel_id'], "message3")

    time.sleep(4)

    message_dict = channel.channel_messages(user1['token'], channel_dict['channel_id'], 0)
    assert len(message_dict['messages']) == 1
    assert message_dict['messages'][0]['message'] == ("bilbobaggins: message1\n" +
                                                      "frodobaggins: message2\n" +
                                                      "mastersauron: message3")

    standup.standup_start(user1['token'], channel_dict['channel_id'], 2)    
    standup.standup_send(user1['token'], channel_dict['channel_id'], "message4")
    standup.standup_send(user2['token'], channel_dict['channel_id'], "message5")
    standup.standup_send(user3['token'], channel_dict['channel_id'], "message6")

    time.sleep(3)
    standup.standup_active(user1['token'], channel_dict['channel_id'])

    message_dict = channel.channel_messages(user1['token'], channel_dict['channel_id'], 0)
    assert len(message_dict['messages']) == 2
    assert message_dict['messages'][0]['message'] == ("bilbobaggins: message4\n" +
                                                      "frodobaggins: message5\n" +
                                                      "mastersauron: message6")
    time.sleep(3)
def test_time_standup():
    """ 
    Tests if standup_start and standup_send works. 
    """
    clear()
    user = auth.auth_register("email1@email.com", "password", "Bilbo", "Baggins")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel['channel_id'], 2)
    
    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], channel['channel_id'], "a"*1001)
   

#####################################################################
#                                                                   #
#                   Standup send                                    #
#                                                                   #
#####################################################################

def test_standup_send_handle():
    """ 
    Tests if standup_start and standup_send works. 
    """
    clear()
    user1 = auth.auth_register("email1@email.com", "password", "Bilbo", "Baggins")
    channel_dict = channels.channels_create(user1['token'], "test_channel", True)
    user.user_profile_sethandle(user1['token'], 'handle')
    standup.standup_start(user1['token'], channel_dict['channel_id'], 3)
    standup.standup_send(user1['token'], channel_dict['channel_id'], "message1")

    time.sleep(5)
    standup.standup_active(user1['token'], channel_dict['channel_id'])
    
    message_dict = channel.channel_messages(user1['token'], channel_dict['channel_id'], 0)
    
    assert message_dict['messages'][0]['message'] == ("handle: message1")
    user.user_profile_sethandle(user1['token'], 'eren')
    standup.standup_start(user1['token'], channel_dict['channel_id'], 3)
    standup.standup_send(user1['token'], channel_dict['channel_id'], "message1")

    time.sleep(5)
    standup.standup_active(user1['token'], channel_dict['channel_id'])
    
    message_dict = channel.channel_messages(user1['token'], channel_dict['channel_id'], 0)
    assert message_dict['messages'][0]['message'] == ("eren: message1")


def test_standupsend_tokenwrong():
    '''
    Invalid token
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 1)
    
    
    with pytest.raises(error.AccessError):
        standup.standup_send('invalid', channel['channel_id'], 'RM')
    time.sleep(2)
    
def test_standupsend_id_invalid():
    '''
    Invalid channel_id
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 1)
    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], "invalid", "Jin")
    time.sleep(2)

def test_standupsend_name_invalid():
    '''
    Invalid channel_id
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 1)
    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], channel["channel_id"], "a"*1001)
    time.sleep(2)



#####################################################################
#                                                                   #
#                   Standup active                                  #
#                                                                   #
#####################################################################


def test_active_standupstart():
    '''
    If standup is active
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 2)
    
    with pytest.raises(error.InputError):
        standup.standup_start(user['token'], channel["channel_id"], 2)
    time.sleep(3)

def test_active_standupactive_token():
    '''
    If standup token is invalid
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 2)

    with pytest.raises(error.AccessError):
        standup.standup_active('token', channel["channel_id"])

    time.sleep(3)
def test_active_standupactive_channel():
    '''
    If standup is active
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 4)

    with pytest.raises(error.InputError):
        standup.standup_active(user['token'], "channel_id")

def test_notactive_standupsend():
    '''
    If standup is not active and try to send
    '''

    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)

    with pytest.raises(error.InputError):
        standup.standup_send(user['token'], channel['channel_id'], "Jin")


def test_active_output2():
    '''
    Test output of active 
    '''
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)

    assert standup.standup_active(user['token'], channel['channel_id']) == {'is_active': False, 'time_finish': None}

def test_active_output3():
    clear()
    user = auth.auth_register("ando@gmail.com", "password", "First", "Last")
    channel = channels.channels_create(user['token'], "name", True)
    standup.standup_start(user['token'], channel["channel_id"], 3)
    assert standup.standup_active(user['token'], channel['channel_id']).get('is_active') == True
    time.sleep(4)
    assert standup.standup_active(user['token'], channel['channel_id']).get('is_active') == False