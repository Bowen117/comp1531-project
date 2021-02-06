'''
Imported files for channel_test.
'''
import pytest
from error import InputError, AccessError 
from channels import channels_create
from auth import auth_register
from channel import channel_invite, channel_details, channel_messages, channel_leave, channel_join, channel_addowner, channel_removeowner
from message import message_send
from other import clear

#################################################################################
#                                                                               #
#                      channel_addowner testing functions                       #
#                                                                               #
#################################################################################

def test_addowner_invalid_channel_id():
    '''
    Testing when channel_id is invalid.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("u_id")
    
    with pytest.raises(InputError):
        channel_addowner(user_token, channel_id, "invalid_id")

def test_addowner_invalid_token_id():
    '''
    Testing when channel_id is invalid.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user1 = auth_register("user1@gmail.com", "password", "Firstname", "Lastname")
    channels_return = channels_create(user['token'], "username", True)
    channel_id = channels_return.get("u_id")
    
    with pytest.raises(InputError):
        channel_addowner('token', channel_id, user1['u_id'])

def test_addowner_no_id():
    '''
    Testing when there is no ID.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    channels_return = channels_create(user_token, "username", True)
    channels_return.get("u_id")
    
    with pytest.raises(InputError):
        channel_addowner(user_token, "", "")

def test_addowner_already_owner():
    '''
    Testing when an owner is being added as an owner to the channel.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user_id = user.get("u_id")
    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("channel_id")
    # channel_join(user_token, channel_id)

    with pytest.raises(InputError):
        channel_addowner(user_token, channel_id, user_id)

def test_addowner_invalid_channel():
    '''
    When the channel is invalid.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user_id = user.get("u_id")

    with pytest.raises(InputError):
        channel_addowner(user_token, "channel_id", user_id)



def test_addowner_not_authorised():
    '''
    When the user being added as owner is not authorised.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user_id = user.get("u_id")
    channel = channels_create(user_token, "username", True)
    channel_id = channel.get("channel_id")

    with pytest.raises(InputError):
        channel_addowner(user_token, channel_id, user_id)

def test_tokenaddowner_not_authorised():
    '''
    When the user being added as owner is not authorised.
    '''
    clear()
    user = auth_register("user1@gmail.com", "password", "Firstname", "Lastname")
    user1 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user2 = auth_register("user3@gmail.com", "password", "Firstname", "Lastname")
    channel = channels_create(user['token'], "username", True)
    channel_id = channel.get("channel_id")

    with pytest.raises(AccessError):
        channel_addowner(user1['token'], channel_id, user2['u_id'])

def test_addowner_working():
    '''
    Testing if channel_addowner is working.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")

    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("channel_id")

    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user2_id = user2.get("u_id")

  
    assert channel_addowner(user_token, channel_id, user2_id) == {}

def test_addowner_multiple_owners():
    '''
    Testing when multiple users are being added as an owner.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")

    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("channel_id")

    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user2_id = user2.get("u_id")

    user3 = auth_register("user3@gmail.com", "password", "Firstname", "Lastname")
    user3_id = user3.get("u_id")

  
    assert channel_addowner(user_token, channel_id, user2_id) == {}
    assert channel_addowner(user_token, channel_id, user3_id) == {}

#################################################################################
#                                                                               #
#                      channel_removeowner testing functions                    #
#                                                                               #
#################################################################################

def test_removeowner_invalid_channel_id():
    '''
    Testing when channel_id is invalid.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("u_id")
    
    with pytest.raises(InputError):
        channel_removeowner(user_token, channel_id, "invalid_id")

def test_removeowner_invalid_token_id():
    '''
    Testing when channel_id is invalid.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")

    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("channel_id")


    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user2_id = user2.get("u_id")
    
    with pytest.raises(InputError):
        channel_removeowner('token', channel_id, user2_id)

def test_removeowner_not_an_owner():
    '''
    Testing when trying to remove a user who isn't an owner from owners of the channel.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")

    channels_return = channels_create(user_token, "username", True)
    channel_id = channels_return.get("channel_id")


    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user2_id = user2.get("u_id")

    with pytest.raises(InputError):
        channel_removeowner(user_token, channel_id, user2_id)

def test_removeowner_invalid_channel():
    '''
    Testing when channel is invalid.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user_id = user.get("u_id")

    with pytest.raises(InputError):
        channel_removeowner(user_token, "channel_id", user_id)

def test_invalid_user_remove():
    '''
    Testing when channel_remove is invalid.
    '''
    clear()
    user2 = auth_register("test2@gmail.com", 'password', 'abcd2', 'efgh2')
    user_token2 = user2.get("token")
    channel = channels_create(user_token2, "Channel1", True)
    channel.get("channel_id")

    user_id = 123123
    
    with pytest.raises(InputError):
        channel_removeowner(user_token2, "channel_id", user_id)

def test_removeowner_not_authorised():
    '''
    Testing when an unauthorised user is being removed as an owner of the channel.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user3 = auth_register("user3@gmail.com", "password", "Firstname", "Lastname")
    user_token = user.get("token")
    user2_token = user2.get("token")
    user_id = user3.get("u_id")
    channel = channels_create(user_token, "username", True)
    channel_id = channel.get("channel_id")

    with pytest.raises(AccessError):
        channel_removeowner(user2_token, channel_id, user_id)

def test_removeowner_flockr_owner():
    '''
    Testing if channel_removeowner works for a flockr owner.
    '''
    clear()
    user = auth_register("user@gmail.com", "password", "Firstname", "Lastname")
    user2 = auth_register("user2@gmail.com", "password", "Firstname", "Lastname")
    user3 = auth_register("user3@gmail.com", "password", "Firstname", "Lastname")

    user_token = user.get("token")
    user2_token = user2.get("token")
    user3_id = user3.get("u_id")

    channel = channels_create(user2_token, "username", True)
    channel_id = channel.get("channel_id")
    channel_addowner(user2_token, channel_id, user3_id)
    channel_id = channel.get("channel_id")
    channel_join(user_token, channel_id)

    assert channel_removeowner(user_token, channel_id, user3_id) == {}

#################################################################################
#                                                                               #
#                      channel_details testing functions                        #
#                                                                               #
#################################################################################
  
def test_details_invalid_channel():
    '''
    Testing when channel is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'pech')
    user_token = user.get("token")
    channels_create(user_token, "a", True)
    with pytest.raises(InputError):
        channel_details(user_token, "invalid channel")

def test_invalid_user():
    '''
    Testing when user is invalid.
    '''
    clear()
    user2 = auth_register("test2@gmail.com", 'password', 'abcd2', 'efgh2')
    user_token2 = user2.get("token")
    channel = channels_create(user_token2, "Channel1", True)
    channel_id = channel.get("channel_id")
    
    invalid_token = 12312312
    
    with pytest.raises(InputError):
        channel_details(invalid_token, channel_id)

def test_details_user_not_authorized():
    '''
    Testing when the user is not authorised.
    '''
    clear()
    user = auth_register("test@gmail.com", 'password', 'abcd', 'efgh')
    user_token = user.get("token")
    user2 = auth_register("test2@gmail.com", 'password', 'abcd2', 'efgh2')
    user_token2 = user2.get("token")
    channel = channels_create(user_token, "Channel1", True)
    channel_id = channel.get("channel_id")

    with pytest.raises(AccessError):
        channel_details(user_token2, channel_id)

def test_details_returns_correct_output():
    '''
    Testing if channel_details works.
    '''
    clear()
    user = auth_register("test@gmail.com", 'password', 'abcd', 'efgh')
    user_token = user.get("token")
    
    user2 = auth_register("test2@gmail.com", 'erenyaegar', 'ijklm', 'nopqrs')
    user_token2 = user2.get("token")

    channel = channels_create(user_token, "Channel1", True)
    channel_id = channel.get("channel_id")
    channel_join(user_token2, channel_id)
    details_channel = channel_details(user_token, channel_id)
    assert len(details_channel.get("all_members")) == 2
    assert details_channel["all_members"][0]["name_first"] == 'abcd'
    assert details_channel["all_members"][1]["name_first"] == 'ijklm'

def test_details_returns_correct_output_for_owner():
    '''
    Testing if channel_details works for owners.
    '''
    clear()
    user = auth_register("test@gmail.com", 'password', 'abcd', 'efgh')
    user_token = user.get("token")
    
    user2 = auth_register("test2@gmail.com", 'erenyaegar', 'ijklm', 'nopqrs')
    user_token2 = user2.get("token")
    user_id2 = user2.get('u_id')

    user3 = auth_register("test3@gmail.com", 'erenyaegar', 'James', 'nopqrs')
    user_token3 = user3.get("token")
    user3.get('u_id')

    channel = channels_create(user_token, "Channel1", True)
    channel_id = channel.get("channel_id")
    channel_join(user_token2, channel_id)
    channel_join(user_token3, channel_id)
    channel_addowner(user_token, channel_id, user_id2)
    details_channel = channel_details(user_token, channel_id)
    assert len(details_channel.get("owner_members")) == 2
    assert details_channel["owner_members"][0]["name_first"] == 'abcd'
    assert details_channel["owner_members"][1]["name_first"] == 'ijklm'
    assert len(details_channel.get("all_members")) == 3
    assert details_channel["all_members"][0]["name_first"] == 'abcd'
    assert details_channel["all_members"][1]["name_first"] == 'ijklm'
    assert details_channel["all_members"][2]["name_first"] == 'James'

#################################################################################
#                                                                               #
#                      channel_invite testing functions                         #
#                                                                               #
#################################################################################

def test_invalid_id():
    '''
    Testing when u_id is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    channels_return = channels_create(user_token, "A", True)
    channel_id = channels_return.get("channel_id")

    with pytest.raises(InputError):
        channel_invite(user_token, channel_id, "invalid_id")

def test_invalid_token_invite():
    '''
    Testing when the token is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    user_id = user.get("u_id")
    channels_return = channels_create(user_token, "A", True)
    channel_id = channels_return.get("channel_id")
    
    with pytest.raises(InputError):
        channel_invite("invalid_token", channel_id, user_id)

def test_u_id_not_inchannel():
    '''
    Testing when the token is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user1 = auth_register("test1@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    channels_return = channels_create(user_token, "A", True)
    channel_id = channels_return.get("channel_id")
    
    with pytest.raises(AccessError):
        channel_invite(user1['token'], channel_id, user.get('u_id'))

def test_u_id_already_inchannel():
    '''
    Testing when the token is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    auth_register("test1@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    channels_return = channels_create(user_token, "A", True)
    channel_id = channels_return.get("channel_id")

    with pytest.raises(AccessError):
        channel_invite(user['token'], channel_id, user.get('u_id'))

def test_invalid_channel():
    '''
    Testing when the channel is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'pech')
    user_token = user.get("token")
    user_id = user.get("u_id")
    channels_create(user_token, "A", True)
    with pytest.raises(InputError):
        channel_invite(user_token, "invalid channel", user_id)

def test_if_invite_working():
    '''
    Testing if channel_invite is working.
    ''' 
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'pech')
    user_token = user.get("token")
    user1 = auth_register("test123@gmail.com", 'erenyaegar1', 'ando2', 'pech')
    user_token1 = user1.get("token")
    user_id = user1.get("u_id")
    channels_return = channels_create(user_token, "A", True)
    channel_id = channels_return.get("channel_id")
    assert channel_invite(user_token, channel_id, user_id) == {}
    channel_info = channel_details(user_token1, channel_id)
    assert channel_info["all_members"][0]["name_first"] == 'ando'
    assert channel_info["all_members"][1]["name_first"] == 'ando2'

def test_valid_invite_public():
    '''
    Testing if channel_invite works if the channel is public.
    '''
    clear()
    user1 = auth_register("email1@email.com", "password", "Michael", "Palin")
    user2 = auth_register("email2@email.com", "password", "Tony", "Stark")

    # User 1 creates a new public channel:
    c_id = channels_create(user1.get('token'), "testChannel", True)

    # User 1 invites User 2 to the channel:
    channel_invite(user1.get('token'), c_id.get('channel_id'), user2.get('u_id'))
    details_after = channel_details(user2["token"], c_id["channel_id"])
    assert details_after["all_members"][0]["u_id"] == user1["u_id"]
    assert details_after["all_members"][1]["u_id"] == user2["u_id"]
    assert len(details_after["all_members"]) == 2
    assert details_after["owner_members"][0]["u_id"] == user1["u_id"]
    assert len(details_after["owner_members"]) == 1

#################################################################################
#                                                                               #
#                      channel_leave testing functions                          #
#                                                                               #
#################################################################################

def test_leave_invalid_channel():
    '''
    Testing when the channel is invalid.
    '''
    clear()
    current_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")

    with pytest.raises(InputError):
        channel_leave(current_user.get('token'), 1)

def test_leave_user_not_from_channel():
    '''
    Testing when a user tries to leave a channel that they are not in.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    channel_detail = channels_create(first_user.get("token"), "channel1", True)

    with pytest.raises(AccessError):
        channel_leave(second_user.get("token"), channel_detail.get("channel_id"))

def test_leave_no_channel():
    '''
    Testing when there isn't a channel to leave.
    '''
    clear()
    first_user = auth_register(
        "test@gmail.com", "password", "Firstname", "Lastname")

    with pytest.raises(InputError):
        channel_leave(first_user.get("token"), "")

def test_leave_invalid_token():
    '''
    Testing when the token is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    channel_detail = channels_create(first_user.get("token"), "channel1", True)
    channel_join(second_user.get("token"), channel_detail.get("channel_id"))

    invalid_token = 123

    with pytest.raises(InputError):
        channel_leave(invalid_token, channel_detail.get("channel_id"))

def test_user_not_from_channel():
    '''
    Testing when user is not from the channel.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    third_user = auth_register("james@gmail.com", "jameyy", "James", "Jameson")
    channel_detail = channels_create(first_user.get("token"), "channel1", True)
    channel_join(second_user.get("token"), channel_detail.get("channel_id"))

    with pytest.raises(AccessError):
        channel_leave(third_user.get("token"), channel_detail.get("channel_id"))

def test_leave_valid_channel():
    '''
    Testing when the channel is valid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    create_channel = channels_create(first_user.get("token"), "channel1", True)
    channel_join(second_user.get("token"), create_channel.get("channel_id"))

    details_channel = channel_details(first_user.get("token"), create_channel.get("channel_id"))
    assert len(details_channel.get("all_members")) == 2


    assert channel_leave(second_user.get('token'), create_channel.get("channel_id")) == {}
    details_channel = channel_details(first_user.get("token"), create_channel.get("channel_id"))
    
    assert len(details_channel.get("all_members")) == 1
    assert details_channel['all_members'][0]["u_id"] == first_user["u_id"]

#################################################################################
#                                                                               #
#                      channel_join testing functions                           #
#                                                                               #
#################################################################################

def test_join_no_channel():
    '''
    Testing when there is not a channel to join.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    channels_create(first_user.get("token"), "channel1", True)

    with pytest.raises(InputError):
        channel_join(second_user.get("token"), "")

def test_join_invalid_channel():
    '''
    Testing when the channel is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    channels_create(first_user.get("token"), "channel1", True)

    invalid_channel_id = 123

    with pytest.raises(InputError):
        channel_join(second_user.get("token"), invalid_channel_id)
   
def test_join_invalid_user():
    '''
    Testing when there is an invalid user trying to join the channel.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    create_channel = channels_create(first_user.get("token"), "channel1", True)
    
    invalid_token = 1231231231
    with pytest.raises(InputError):
        channel_join(invalid_token, create_channel.get("channel_id"))

def test_join_valid():
    '''
    Testing if channel_join works.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    create_channel = channels_create(first_user.get("token"), "channel1", True)
    channel_join(second_user.get("token"), create_channel.get("channel_id"))

    details_channel = channel_details(first_user.get("token"), create_channel.get("channel_id"))
    print(details_channel)
    assert len(details_channel["all_members"]) == 2
    assert details_channel["all_members"][0]["u_id"] == first_user["u_id"]
    assert details_channel["all_members"][1]["u_id"] == second_user["u_id"]

    third_user = auth_register("jenny@gmail.com", "jennyy", "Jen", "Jenson")
    channel_join(third_user.get("token"), create_channel.get("channel_id"))

    details_channel = channel_details(first_user.get("token"), create_channel.get("channel_id"))
    assert len(details_channel.get("all_members")) == 3
    assert details_channel["all_members"][0]["u_id"] == first_user["u_id"]
    assert details_channel["all_members"][1]["u_id"] == second_user["u_id"]
    assert details_channel["all_members"][2]["u_id"] == third_user["u_id"]

def test_joining_private():
    '''
    Testing when trying to join a private channel.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    create_channel = channels_create(first_user.get("token"), "channel1", False)
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")

    with pytest.raises(AccessError):
        channel_join(second_user.get("token"), create_channel.get("channel_id"))

#################################################################################
#                                                                               #
#                      channel_messages testing functions                       #
#                                                                               #
#################################################################################


def test_0_msg():
    '''
    Testing when token is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    channel = channels_create(first_user.get("token"), "channel1", True)
   
    assert channel_messages(first_user['token'], channel.get("channel_id"), 0) == {"messages": [], "start": 0, "end": -1}



def test_invalid_token():
    '''
    Testing when token is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    channel = channels_create(first_user.get("token"), "channel1", True)
    with pytest.raises(InputError):
        channel_messages("invalid_token", channel.get("channel_id"), 0)

def test_messages_channel_invalid():
    '''
    Testing when the channel is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    channels_create(first_user.get("token"), "channel1", True)
    
    with pytest.raises(InputError):
        channel_messages(first_user.get("token"), "Invalid_channel", 0)

def test_messages_start_greater_end():
    '''
    Testing when the channel is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    create_channel = channels_create(first_user.get("token"), "channel1", True)
    
    with pytest.raises(InputError):
        channel_messages(first_user.get("token"), create_channel.get("channel_id"), 50)

def test_messages_user_invalid():
    '''
    Testing when the user is invalid.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    second_user = auth_register("john@gmail.com", "johnny", "John", "Johnson")
    create_channel = channels_create(first_user.get("token"), "channel1", True)

    with pytest.raises(AccessError):
        channel_messages(second_user.get("token"), create_channel.get("channel_id"), 0)

def test_messages_if_working():
    '''
    Testing if channel_messages work.
    '''
    clear()
    first_user = auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    create_channel = channels_create(first_user.get("token"), "channel1", True)
    message_send(first_user['token'], create_channel['channel_id'], "First message")
    assert channel_messages(first_user.get("token"), create_channel.get("channel_id"), 0)['messages'][0].get('message') == "First message"

def test_invalid_token_messages():
    '''
    Testing when token is invalid.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    user_id = user.get("u_id")
    channels_return = channels_create(user_token, "A", True)
    channel_id = channels_return.get("u_id")
    
    with pytest.raises(InputError):
        channel_messages("invalid_token", channel_id, user_id)

def test_return_message():
    '''
    Testing the return.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    channel_id = channels_create(user_token, "channel1", True).get('channel_id')
    message_send(user_token, channel_id, "First message")
    message_send(user_token, channel_id, "Recent message")
    assert channel_messages(user_token, channel_id, 0)['messages'][0].get('message') == "Recent message"

def test_return_morethan50message():
    '''
    Testing when there are more than 50 messages.
    '''
    clear()
    user = auth_register("test@gmail.com", 'erenyaegar', 'ando', 'ackermann')
    user_token = user.get("token")
    channel_id = channels_create(user_token, "channel1", True).get('channel_id')
    counter = 60
    while counter >= 0:
        message_send(user_token, channel_id, f"{counter}")
        counter -= 1
  
    assert channel_messages(user_token, channel_id, 10).get('end') == 60
    assert channel_messages(user_token, channel_id, 10)['messages'][0].get('message') == "10"
    assert channel_messages(user_token, channel_id, 10)['messages'][10].get('message') == "20"

    assert channel_messages(user_token, channel_id, 0)['messages'][49].get('message') == "49"




