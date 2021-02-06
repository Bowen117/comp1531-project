'''
File with helper functions to help with code
'''

import auth
import channels 

def check_token(token):
    '''
    Returns dictionary with u_id and status of token
    '''
    #If token valid
    token_status = True 
    for user in auth.registered_tokens:
        if user.get('token') == token:
            token_status = False
            u_id = user.get('u_id')
            return {'token_status': token_status, 'u_id': u_id}
    
    return {'token_status': token_status, 'u_id': None}

def check_channelid_valid(channel_id):
    '''
    Return booleon on channel_id being valid or not
    '''
    #Checked invalid channel
    for curr_channels in channels.channel_data:
        if curr_channels.get('channel_id') == channel_id:
            return False 

    return True

def check_uid_valid(u_id):
    '''
    Return booleon on u_id being valid or not
    '''
    for user in auth.registered_users: 
        if user.get('u_id') == u_id:
            return  False
    
    return True

def check_uid_owner_in_channel(u_id, channel_id):
    '''
    Return booelon on u_id is owner or not
    '''
    for user in channels.channel_data:
        if user.get("channel_id") == channel_id:
            for owner in user.get("owner_ids"):
                if owner == u_id:
                    return False 

    return True

def check_u_id_in_channel(u_id, channel_id):
    '''
    Return booelon on u_id is member or not
    '''
    for user in channels.channel_data:
        if user.get("channel_id") == channel_id:
            for owner in user.get("member_ids"):
                if owner == u_id:
                    return False 

    return True



