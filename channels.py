'''
Imported files for channels.
'''
import auth
import error
import helper_functions

list_of_all_channels = []
channel_data = [] # the status, owner id, member id, channel id, messages

def channels_list(token):
    '''
    Provides a list of all the channels and their details that the authorised user is part of.
    '''

    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    user_id = helper_functions.check_token(token).get('u_id')
    
    # List of channels that the user belongs to 
    user_channel = []
    
    # Checking if the user is in the channel then append that channel to the user channel list
    for channel in list_of_all_channels:            
        channel_id = channel.get("channel_id")     
        for data in channel_data:                   
            if data['channel_id'] == channel_id:    
                if user_id in data['member_ids']:   
                    user_channel.append(channel)    

    return {'channels': user_channel}

def channels_listall(token):
    '''
    Provides a list of all the channels and their details.
    '''
   
    #Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")
    
    # Returning the list of channels
    
    # output = {'channels': []}
    # for channels_d in channel_data:
    #     if channels_d['is_public'] == True:
    #         detail = {
    #             'channel_id': channels_d['channel_id'],
    #             'name': channels_d['name']
    #         }
    #         output['channels'].append(detail)

    
    return {'channels': list_of_all_channels}

def channels_create(token, name, is_public):
    '''
    Creates a new channel that is either public or private.
    '''
    # Checking for a valid token 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")
    
    user_id = helper_functions.check_token(token).get('u_id')

    # Error is the channel is greater than 20
    if len(name) > 20:
        raise error.InputError("The channel name you have entered is greater than 20 characters.")
    
    # Error if theres no channel name
    if len(name) == 0:
        raise error.InputError("No channel name entered.")   
    
    # Assigning the channel id as the number of channels 
    number_of_channels = len(list_of_all_channels)
    channel_id = number_of_channels + 1
    
    channels_details = {
        'channel_id': channel_id,
        'name': name
    }

    channel_data_base = {
        'owner_ids': [],
        'member_ids': [],
        'channel_id': channel_id,
        'is_public': True,
        'messages': [],
        'name': name
    }
    
    # Assigning whether the channels is public or private
    channel_data_base['is_public'] = is_public

    # Adding the data of the channel
    for user in auth.registered_tokens:
        if token == user.get("token"):
            user_id = user.get("u_id")
            channel_data_base['owner_ids'].append(user_id)
            channel_data_base['member_ids'].append(user_id)

    # Adding the newly created channel into the list
    channel_data.append(channel_data_base)
    list_of_all_channels.append(channels_details)

    return {'channel_id': channel_id}