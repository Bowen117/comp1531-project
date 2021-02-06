'''
Imported files for channels_test.
'''
import pytest
import error
from channels import channels_create, channels_list, channels_listall
from channel import channel_join
from auth import auth_register
from other import clear

#################################################################################
#                                                                               #
#                      channels_list testing functions                          #
#                                                                               #
#################################################################################

def test_invalid_token():
    '''
    Testing when token is invalid.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")

    channels_create(user_1_token, "usernameone", True)
    invalid_token = 112312
    with pytest.raises(error.InputError):
        channels_list(invalid_token)

def test_user_in_no_channels():
    '''
    Testing when the user is not in any channel.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")
    assert channels_list(user_1_token).get('channels') == []

def test_valid_channel_list():
    '''
    Testing if channel_list works.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")
    user_2 = auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_token = user_2.get("token")
    auth_register("userthree@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_3_token = user_2.get("token")
    auth_register("userfour@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_4_token = user_2.get("token")

    channel1 = channels_create(user_1_token, "channel1", True) 
    channel2 = channels_create(user_1_token, "channel2", True)
    channel3 = channels_create(user_1_token, "channel3", True) 
    channels_create(user_2_token, "channel4", True)
    channels_create(user_3_token, "channel5", True)
    channels_create(user_4_token, "channel6", True)

    channel_list = channels_list(user_1_token)

    assert channel_list.get('channels')[0]["channel_id"] == channel1.get("channel_id")
    assert channel_list.get('channels')[1]["channel_id"] == channel2.get("channel_id")
    assert channel_list.get('channels')[2]["channel_id"] == channel3.get("channel_id")
    assert len(channel_list.get('channels')) == 3

def test_user_one_channel():
    '''
    Testing when the user is only in one channel.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")
    user_2 = auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_token = user_2.get("token")

    channels_create(user_1_token, "channel1", True)
    channels_create(user_1_token, "channel2", True)
    channels_create(user_1_token, "channel3", True)
    channel4 = channels_create(user_2_token, "channel4", True) 

    channel_list = channels_list(user_2_token).get('channels')

    assert channel_list[0]["channel_id"] == channel4.get("channel_id")
    assert len(channel_list) == 1

def test_list_both_private_public_channels():
    '''
    Testing when the user is in both public and private channels.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")
    user_2 = auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_token = user_2.get("token")

    channel1 = channels_create(user_1_token, "channel1", True)
    channel2 = channels_create(user_1_token, "channel2", False)
    channel3 = channels_create(user_1_token, "channel3", True)
    channels_create(user_2_token, "channel4", True)

    channel_list = channels_list(user_1_token).get('channels')

    assert channel_list[0]["channel_id"] == channel1.get("channel_id")
    assert channel_list[1]["channel_id"] == channel2.get("channel_id")
    assert channel_list[2]["channel_id"] == channel3.get("channel_id")
    assert len(channel_list) == 3
    
########################################################################
#                                                                      #
#                    channels_listall testing functions                #
#                                                                      #
########################################################################

def test_valid_listall_channel():
    '''
    Testing if channel_listall works.
    '''
    clear()
    
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")
    user_2 = auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_token = user_2.get("token")

    channel1 = channels_create(user_1_token, "channel1", True)
    channel2 = channels_create(user_1_token, "channel22", True)
    channel3 = channels_create(user_1_token, "channel3", False)
    channel4 = channels_create(user_1_token, "channel4", False)
    
    channel_join(user_2_token, channel1.get("channel_id"))
    channel_join(user_2_token, channel2.get("channel_id"))
    
    channel_list = channels_listall(user_1_token).get('channels')
    
    assert channel_list[0]["channel_id"] == channel1.get("channel_id")
    assert channel_list[1]["channel_id"] == channel2.get("channel_id")
    assert channel_list[2]["channel_id"] == channel3.get("channel_id")
    assert channel_list[3]["channel_id"] == channel4.get("channel_id")
    assert len(channel_list) == 4
    
def test_channels_no_channels():
    '''
    Testing when there are no channels.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")

    assert channels_listall(user_1_token).get('channels') == []
    
def test_channel_listall_user_not_in_a_channel():
    '''
    Testing when user not in a channel.
    '''
    clear()
    valid_viewer = auth_register("useronee@gmail.com", "passwordOne", "Firstone", "Lastone")
    valid_viewer_token = valid_viewer.get("token")

    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")

    user_2 = auth_register("usertwo@gmail.com", "passwordTwo", "Firsttwo", "Lasttwo")
    user_2_token = user_2.get("token")
    channel1 = channels_create(user_1_token, "channel1", True)
    
    
    channel_join(user_2_token, channel1.get("channel_id"))
    
    channel_list = channels_listall(valid_viewer_token).get('channels')
    
    assert channel_list[0]["channel_id"] == channel1.get("channel_id")
    assert len(channel_list) == 1

def test_channels_invalid_token():
    '''
    Testing when the token is invalid.
    '''
    clear()
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")

    channels_create(user_1_token, "channel1", True)
    invalid_token = 123
    with pytest.raises(error.InputError):
        channels_listall(invalid_token) 
   
def test_channels_listall_private():
    '''
    Testing when the channels are private.
    '''
    clear()
    valid_viewer = auth_register("useronee@gmail.com", "passwordOne", "Firstone", "Lastone")
    valid_viewer_token = valid_viewer.get("token")

    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")

    channel1 = channels_create(user_1_token, "channel1", True)
    channel2 = channels_create(user_1_token, "channel2", False)
    channel3 = channels_create(user_1_token, "channel3", False)
    channel4 = channels_create(user_1_token, "channel4", False)
    
    channel_list = channels_listall(valid_viewer_token).get('channels')
    
    assert channel_list[0]["channel_id"] == channel1.get("channel_id")
    assert channel_list[1]["channel_id"] == channel2.get("channel_id")
    assert channel_list[2]["channel_id"] == channel3.get("channel_id")
    assert channel_list[3]["channel_id"] == channel4.get("channel_id")
    assert len(channel_list) == 4

def test_only_one_channel():
    '''
    Testing when there is only one channel.
    '''
    clear()
    valid_viewer = auth_register("useronee@gmail.com", "passwordOne", "Firstone", "Lastone")
    valid_viewer_token = valid_viewer.get("token")
    user_1 = auth_register("userone@gmail.com", "passwordOne", "Firstone", "Lastone")
    user_1_token = user_1.get("token")

    channel1 = channels_create(user_1_token, "channel1", True)
    channel_list = channels_listall(valid_viewer_token).get('channels')
    
    assert channel_list[0]["channel_id"] == channel1.get("channel_id")
    assert len(channel_list) == 1

########################################################################
#                                                                      #
#                    channels_create testing functions                 #
#                                                                      #
########################################################################

def test_create_more_than_one_channel():
    '''
    Testing when more than one channel is being created.
    '''
    clear()
    new_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    user_token = new_user.get("token")
    new_channel_id1 = channels_create(user_token, "channel1", True)    
    new_channel_id2 = channels_create(user_token, "channel2", True) 
    new_channel_id3 = channels_create(user_token, "channel3", True) 
    new_channel_id4 = channels_create(user_token, "channel4", True) 

    
    list_of_channels = channels_list(user_token).get('channels') 
    assert list_of_channels[0]["channel_id"] == new_channel_id1["channel_id"]
    assert list_of_channels[0]["name"] == "channel1"
    assert list_of_channels[1]["channel_id"] == new_channel_id2["channel_id"]
    assert list_of_channels[1]["name"] == "channel2"
    assert list_of_channels[2]["channel_id"] == new_channel_id3["channel_id"]
    assert list_of_channels[2]["name"] == "channel3"
    assert list_of_channels[3]["channel_id"] == new_channel_id4["channel_id"]
    assert list_of_channels[3]["name"] == "channel4"

def test_create_one_channel():
    '''
    Testing when one channel is being created.
    '''
    clear()
    new_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    user_token = new_user.get("token")

    new_channel_id1 = channels_create(user_token, "channel1", True)  
    
    list_of_channels = channels_list(user_token).get('channels') 
    assert list_of_channels[0]["channel_id"] == new_channel_id1["channel_id"]
    assert list_of_channels[0]["name"] == "channel1"

def test_create_public():
    '''
    Testing when a public channel is being created.
    '''
    clear()
    new_user = auth_register("user@gmail.com", "userpass", "User", "Lastname")
    user_token = new_user.get("token")

    new_channel_id = channels_create(user_token, "channel1", True)    
    
    list_of_channels = channels_list(user_token).get('channels') 
    assert list_of_channels[0]["channel_id"] == new_channel_id["channel_id"]
    assert list_of_channels[0]["name"] == "channel1"

def test_create_private():
    '''
    Testing when a private channel is being created.
    '''
    clear()
    new_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    user_token = new_user.get("token")
    new_channel_id = channels_create(user_token, "channel1", False)    
    
    list_of_channels = channels_list(user_token).get('channels') 
    assert list_of_channels[0]["channel_id"] == new_channel_id["channel_id"]
    assert list_of_channels[0]["name"] == "channel1"

def test_name_more_than20_characters_private():
    '''
    Testing when the channel name for a private channel is more than 20 characters.
    '''
    clear()
    new_user = auth_register("user@gmail.com", "userpass", "User", "Lastname")
    user_token = new_user.get("token")
    with pytest.raises(error.InputError):
        channels_create(user_token, "a"*30, False)

def test_name_more_than20_characters_public():
    '''
    Testing when the channel name for a public channel is more than 20 characters.
    '''
    clear()
    new_user = auth_register("user@gmail.com", "userpass", "User", "Lastname")
    user_token = new_user.get("token")
    with pytest.raises(error.InputError):
        channels_create(user_token, "a"*30, True)

def test_no_channel_name():
    '''
    Testing when there is no channel name.
    '''
    clear()
    new_user = auth_register("user@gmail.com", "userpass", "User", "Lastname")
    user_token = new_user.get("token")
    with pytest.raises(error.InputError):
        channels_create(user_token, "", True)

def test_invalid_create_public_token():
    '''
    Testing when token is invalid for creating a public channel.
    '''
    clear()
    invalid_user_token = 1
    with pytest.raises(error.InputError):
        channels_create(invalid_user_token, "channel_name", True) 

def test_invalid_create_private_token():
    '''
    Testing when token is invalid for creating a private channel.
    '''
    clear()
    invalid_user_token = 1
    with pytest.raises(error.InputError):
        channels_create(invalid_user_token, "channel_name", False)
