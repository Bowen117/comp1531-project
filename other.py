'''
Imported files for other.
'''
import re
import auth
import channels
import channel
import message
import error
import standup
import helper_functions

def clear():
    '''
    Resets the internal data of the application to it's initial state.
    '''
    auth.registered_users = []
    auth.registered_tokens = []
    auth.reset_codes = []
    channels.list_of_all_channels = []
    channels.channel_data = []
    channel.registered_channels = []
    message.message_ids = []
    standup.STANDUPS = []
    standup.CHANNELSMSG = {}

def users_all(token):
    '''
    Returns a list of all users and their associated details
    '''
    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")

    # Returning all users and their details
    all_user_detail = []
    for users in auth.registered_users:
        user_detail = {
                'u_id': users.get('u_id'),
                'email': users.get('email'),
                'name_first': users.get('first_name'),
                'name_last': users.get('last_name'),
                'handle_str': users.get('handle'),
                'profile_img_url': users.get('profile_img_url'),
            }
        all_user_detail.append(user_detail)
    return {'users' : all_user_detail}

def admin_userpermission_change(token, u_id, permission_id):
    '''
    Changes the permissions of the u_id entered.
    '''
    #If permission_id invalid
    if permission_id < 1 or permission_id > 2:
        raise error.InputError(description="permission_id invalid")

    # check for valid user:
    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    token_uid = helper_functions.check_token(token).get('u_id')
    
    #If u_id valid
    if helper_functions.check_uid_valid(u_id):
        raise error.InputError(description="Invalid u_id")


    #If token is not owner
    not_owner = True
    for user in auth.registered_users:
        if user.get("u_id") == token_uid:
            if user.get("permissions") == 1:
                not_owner = False
                break 

    if not_owner:
        raise error.AccessError("Authorised user is not owner")
    
    #Update u_id permissions
    for user in auth.registered_users:
        if user.get("u_id") == u_id:
            user["permissions"] = permission_id
            break

    #If member in channel also add to owner
    if permission_id == 1:
        for data in channels.channel_data:
            if u_id in data.get('member_ids'):
                if u_id not in data.get('owner_ids'):
                    data.get('owner_ids').append(u_id)

    return {}    

def search(token, query_str):
    '''
    Searches all channel messages and uses regex to find similar messages.
    '''
    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    u_id = helper_functions.check_token(token).get('u_id')

    messages = []

    #return dictionary of details of query string
    for chan in channels.channel_data:
        for user in chan.get("member_ids"):
            if user == u_id:
                for line in chan.get("messages"):
                    if line.get('message_sent') is None:
                        break
                    
                    #Seeing if user has reacted
                    is_this_user_reacted = False

                    if u_id in line.get('reacts')[0]['u_ids']:
                        is_this_user_reacted = True 

                    if re.search(str(query_str), line.get('message_sent')):
                        msg = {
                            'message_id': line.get('message_id'),
                            'u_id': line.get('user_id'),
                            'message': line.get('message_sent'),
                            'time_created': line.get('time_created'),
                            'reacts': [{
                                'react_id': line.get('reacts')[0].get('react_id'),
                                'u_ids': line.get('reacts')[0].get('u_ids'),
                                'is_this_user_reacted': is_this_user_reacted,
                            }],
                            'is_pinned': line.get('is_pinned'),
                        }

                        messages.append(msg)
                   

    return {'messages': messages}
