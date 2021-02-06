'''
Imported files for other_test.
'''
import pytest
from error import InputError, AccessError 
from channels import channels_create
from auth import auth_register
from channel import channel_join, channel_addowner, channel_removeowner
from other import clear, users_all, admin_userpermission_change, search
from message import message_send, message_edit, message_remove

#################################################################################
#                                                                               #
#                          users_all testing functions                          #
#                                                                               #
#################################################################################
def test_token_user_all():
    '''
    TOken invalid
    '''
    clear()
    auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    with pytest.raises(AccessError):
        users_all('invalid')

def test_working():
    '''
    Testing if users_all works.
    '''
    clear()
    user_1 = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    all_users = users_all(user_1.get('token')).get('users')

    assert all_users[0]['u_id'] == user_1.get('u_id')
    assert all_users[0]['email'] == "user@gmail.com"
    assert all_users[0]['name_first'] == "Firstname"
    assert all_users[0]['name_last'] == "Lastname"
    assert all_users[0]['handle_str'] == 'firstnamelastname'

def test_working_multiple_users():
    '''
    Testing if users_all works when there are multiple users.
    '''
    clear()
    user_1 = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_2 = auth_register("user2@gmail.com", "password2", "Firstname2", "Lastname2")
    all_users = users_all(user_1.get('token')).get('users')

    assert all_users[0]['u_id'] == user_1.get('u_id')
    assert all_users[0]['email'] == "user@gmail.com"
    assert all_users[0]['name_first'] == "Firstname"
    assert all_users[0]['name_last'] == "Lastname"
    assert all_users[0]['handle_str'] == 'firstnamelastname'
    assert all_users[1]['u_id'] == user_2.get('u_id')
    assert all_users[1]['email'] == "user2@gmail.com"
    assert all_users[1]['name_first'] == "Firstname2"
    assert all_users[1]['name_last'] == "Lastname2"
    assert all_users[1]['handle_str'] == 'firstname2lastname2'

#################################################################################
#                                                                               #
#                          search testing functions                             #
#                                                                               #
#################################################################################
def test_token_token():
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    channels_return = channels_create(user.get('token'), "username", True)
    channels_return.get("channel_id")
    message_send(user.get('token'), channels_return.get('channel_id'), "Testthismessage").get("message_id")

    with pytest.raises(AccessError):
        search("invalid", "Test")

def test_search():
    '''
    Testing if search works.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user_id = user.get("u_id")

    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("channel_id")
    message_id = message_send(user_token, channel_id, "Testthismessage").get("message_id")

    return_search = search(user_token, "Test").get('messages')

    assert return_search[0].get('message_id') == message_id
    assert return_search[0].get('u_id') == user_id
    assert return_search[0].get('message') == 'Testthismessage'

def test_search_2_channels():
    '''
    Testing if search works when searching in two channels.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user_id = user.get("u_id")

    channels_return = channels_create(user_token, "channel1", True)
    channel_id1 = channels_return.get("channel_id")
    message_id1 = message_send(user_token, channel_id1, "Testthismessage").get("message_id")

    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user2_token = user2.get("token")
    user_id2 = user2.get("u_id")

    channel_id2 = channels_create(user2_token, "channel2", True).get("channel_id")
    message_id2 = message_send(user2_token, channel_id2, "Testmsg").get("message_id")

    channel_join(user_token, channel_id2)

    return_search = search(user_token, "Test").get('messages')
    assert return_search[0].get('message_id') == message_id1
    assert return_search[0].get('u_id') == user_id
    assert return_search[0].get('message') == 'Testthismessage'

    assert return_search[1].get('message_id') == message_id2
    assert return_search[1].get('u_id') == user_id2
    assert return_search[1].get('message') == 'Testmsg'

#################################################################################
#                                                                               #
#                   admin_userpermission_change testing functions               #
#                                                                               #
#################################################################################
def test_token_invalid():
    '''
    Testing when oken is invalid.
    '''
    clear()
    # first user should automatically become a flockr owner
    user_1 = auth_register("oneuser@gmail.com", "passwordOne", "Firstone", "Lastone")
  
    # put random user id as input:     
    with pytest.raises(AccessError):
        admin_userpermission_change('token', user_1.get('u_id'), 1)

def test_invalid_user():
    '''
    Testing when user is invalid.
    '''
    clear()
    # first user should automatically become a flockr owner
    user_1 = auth_register("oneuser@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')
  
    # put random user id as input:     
    with pytest.raises(InputError):
        admin_userpermission_change(user_1_token, 123, 1)

def test_non_owner_access():
    '''
    Testing a non-owner trying to use permission change.
    '''
    clear()
    auth_register("genshinone@gmail.com", "passwordOne", "Firstone", "Lastone")
    
    user_2 = auth_register("genshintwo@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_2_token = user_2.get('token')
    
    user_3 = auth_register("genshinthree@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_3_id = user_3.get('u_id')

    with pytest.raises(AccessError):
        admin_userpermission_change(user_2_token, user_3_id, 1)

def test_invalid_id():
    '''
    Testing invalid permission_id.
    '''
    clear()
    user_1 = auth_register("genshinfour@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')

    user_2 = auth_register("genshinfive@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_id = user_2.get('u_id')

    with pytest.raises(InputError):
        admin_userpermission_change(user_1_token, user_2_id, 3)

def test_permission_addowner():
    '''
    If permissions is changed then no error should be raised.
    '''
    clear()
    #flock owner
    user_1 = auth_register("ando@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')

    #change permissions to flock owner
    user_2 = auth_register("donald@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_id = user_2.get('u_id')
    user_2_token = user_2.get('token')

    #add as channel owner
    user_3 = auth_register("biden@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_3_id = user_3.get('u_id')

    #make user 2 become owner
    admin_userpermission_change(user_1_token, user_2_id, 1)

    channel = channels_create(user_1_token, "channel1", True)
    
    channel1_id = channel.get("channel_id") 

    channel_join(user_2_token, channel1_id)

    channel_addowner(user_2_token, channel1_id, user_3_id)

def test_permissions_removeowner():
    '''
    If permissions updated then no errors raised when removing.
    '''
    clear()
    #flock owner
    user_1 = auth_register("ando@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get('token')

    #change permissions to flock owner
    user_2 = auth_register("donald@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_id = user_2.get('u_id')
    user_2_token = user_2.get('token')

    #add as channel owner
    user_3 = auth_register("biden@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_3_id = user_3.get('u_id')

    #make user 2 become owner
    admin_userpermission_change(user_1_token, user_2_id, 1)

    channel = channels_create(user_1_token, "channel1", True)
    
    channel1_id = channel.get("channel_id") 

    channel_join(user_2_token, channel1_id)

    channel_addowner(user_1_token, channel1_id, user_3_id)

    channel_removeowner(user_2_token, channel1_id, user_3_id)

def test_remove_flocker_owner_access():
    '''
    Testing for a valid message removed by a flockr owner.
    '''
    clear()
    user = auth_register("email@gmail.com", "password", "First", "Last")
    user_1 = auth_register("email1@gmail.com", "password", "First_1", "Last_1")
    channel_1 = channels_create(user.get('token'), 'channel_1', True)
    channel_join(user_1.get('token'), channel_1.get('channel_id'))
    message_info = message_send(user_1.get('token'), channel_1.get('channel_id'), 'Hello world')

    admin_userpermission_change(user.get('token'), user_1.get("u_id"), 1)

    message_remove(user_1.get('token'), message_info.get('message_id'))

def test_flocker_owner_access_other():
    '''
    Testing for a valid message edited by a flocker owner.
    '''
    clear()
    user = auth_register("test_email0@gmail.com", "password", "User_0", "User_last_0")
    user_1 = auth_register("test_email1@gmail.com", "password", "User_1", "User_last_1")
    channel_1 = channels_create(user.get('token'), 'channel_1', True)
    channel_join(user_1.get("token"), channel_1.get("channel_id"))
    admin_userpermission_change(user.get('token'), user_1.get("u_id"), 1)

    message_info = message_send(user.get('token'), channel_1.get('channel_id'), 'Hello world')
    message_edit(user_1.get('token'), message_info.get('message_id'), 'Hellooo Worlldddd!!!!')
  