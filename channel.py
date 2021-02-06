'''
Imported files for channel.
'''
import auth 
import channels 
import error
import helper_functions


""
"ONLY ONE DATA STRUCTURE CHANNEL_DATA_BASE"
"A list consisting of dictionaries"
""

#channel_data = [ {
#        'owner_ids': [],
#        'member_ids': [{
#          }],
#        'channel_id': channel_id,
#        'is_public': True,
#        'messages': [
#           'message_sent': message,
#           'message_id': gen_id,
#           'user_id': user_id,
#           'time_created': time_create,
#           'reacts': [
#               'react_id: 1 (always 1, never changes)
#               'u_ids: [],
#           ],
#           'is_pinned': False (True when pinned),
#         ]
#    }
#        'name': name_of_channel
#    }
#    ]


#For this we need to append u_id to channel_data_base { 'member_id = []}
def channel_invite(token, channel_id, u_id):
    '''
    Inviting a user to join the channel.
    '''
    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")
    
    # user id is not valid 
    if helper_functions.check_uid_valid(u_id):
        raise error.InputError("User not valid")

    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    auth_id = helper_functions.check_token(token).get('u_id')

    #If token is in channel
    if helper_functions.check_u_id_in_channel(auth_id, channel_id):
        raise error.AccessError("Authorised user not in channel")
    
    #User already in channel 
    if helper_functions.check_u_id_in_channel(u_id, channel_id) == False:
        raise error.AccessError("Already in channel")

    # add to user to channel if everything is valid 
    # details_user =  {u_id, email, name_first, name_last, handle_str}   
    for user in channels.channel_data:
        if user.get("channel_id") == channel_id: 
            user["member_ids"].append(u_id)
            break

    return {}

#Use channel_data_base. 
def channel_details(token, channel_id):
    '''
    Presenting the details of the channel.
    '''
    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")
    
    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    user_id = helper_functions.check_token(token).get('u_id')

    #User already in channel 
    if helper_functions.check_u_id_in_channel(user_id, channel_id):
        raise error.AccessError("Not in channel")

    #return details about channel  
    channel_detail = {
        'name': 'name',
        'owner_members': [],
        'all_members': [],
    }
    
    for curr_channels in channels.list_of_all_channels:
        if curr_channels.get('channel_id') == channel_id:
            channel_detail['name'] = curr_channels['name']
            break

    for curr_channels in channels.channel_data:
        if curr_channels.get('channel_id') == channel_id:
            user_ids = curr_channels.get("member_ids")
            for user in user_ids:
                for user_detail in auth.registered_users:
                    if user_detail['u_id'] == user:
                        member_details = {
                            'u_id': user,
                            'name_first': user_detail['first_name'],
                            'name_last': user_detail['last_name'],
                            'profile_img_url': user_detail['profile_img_url'],
                        }
                        channel_detail['all_members'].append(member_details)

    for curr_channels in channels.channel_data:
        if curr_channels.get('channel_id') == channel_id:
            user_ids = curr_channels.get("owner_ids")
            for user in user_ids:
                for user_detail in auth.registered_users:
                    if user_detail['u_id'] == user:
                        owner_details = {
                            'u_id': user,
                            'name_first': user_detail['first_name'],
                            'name_last': user_detail['last_name'],
                            'profile_img_url': user_detail['profile_img_url'],
                        }
                        channel_detail['owner_members'].append(owner_details)
                             
    return channel_detail 

def channel_messages(token, channel_id, start):
    '''
    Return up to 50 messages.
    '''
    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")
    

    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    u_id = helper_functions.check_token(token).get("u_id")
    
    #User already in channel 
    if helper_functions.check_u_id_in_channel(u_id, channel_id):
        raise error.AccessError("Not in channel")

    #return messages 
    for channel in channels.channel_data:
        if channel.get("channel_id") == channel_id:
            messages = channel.get("messages")
            messages = list(reversed(messages))
            num_messages = len(messages)

    if num_messages == 0 and start == 0:
        return {"messages": [], "start": start, "end": -1}

    #If start is larger than number of items in messages
    if start >= num_messages:
        raise error.InputError("Start value older than latest message")
    
    #Append message to a list
    index_message = start
    end = int(index_message) + 50
    counter = 0
    return_messages = []

    
    while counter < 50:
        get_index = start + counter
        if get_index >= end or get_index >= num_messages:
            break

        #Seeing if user has reacted
        is_this_user_reacted = False

        if u_id in messages[get_index].get('reacts')[0]['u_ids']:
            is_this_user_reacted = True 
            
        newmsg = {
            'message_id': messages[get_index].get('message_id'),
            'u_id': messages[get_index].get('user_id'),
            'message': messages[get_index].get('message_sent'),
            'time_created': messages[get_index].get('time_created'),
            'reacts': [{ 
                'react_id': messages[get_index].get('reacts')[0].get('react_id'),
                'u_ids': messages[get_index].get('reacts')[0].get('u_ids'),   
                'is_this_user_reacted': is_this_user_reacted,
            }],
            'is_pinned':messages[get_index].get('is_pinned')
        }
        return_messages.append(newmsg)
        counter += 1
                
    if counter < 50:
        end = -1

    return {"messages": return_messages, "start": start, "end": end}

#Use channel_data_base. Simply have to remove u_id from all_members. 
def channel_leave(token, channel_id):
    '''
    When a user leaves the channel.
    '''
    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    user_id = helper_functions.check_token(token).get("u_id")
    
    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")


    #User already in channel 
    if helper_functions.check_u_id_in_channel(user_id, channel_id):
        raise error.AccessError("Already in channel")

    for current_channel in channels.channel_data:
        if current_channel.get("channel_id") == channel_id:
            for members in current_channel.get("member_ids"):
                if user_id == members:
                    current_channel["member_ids"].remove(user_id)
                    break
            break

    return {}

#Using channel_data_base. Add u_id to all_members
def channel_join(token, channel_id):
    '''
    When a user joins the channel.
    '''
    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    user_id = helper_functions.check_token(token).get("u_id")
    
    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")
    
    # channel is private 
    channel_is_public = False
    for chan_status in channels.channel_data: 
        if chan_status['channel_id'] == channel_id:
            if chan_status['is_public'] == True:
                channel_is_public = True 
                break
    
    if channel_is_public == False: 
        raise error.AccessError("Channel is private")
    
    #If flock owner add to owner
    for user in auth.registered_users:
        if user.get('u_id') == user_id:
            if user.get('permissions') == 1:
                    #Append u_id to list of owners
                    for user in channels.channel_data:
                        if user.get("channel_id") == channel_id:
                             user.get("owner_ids").append(user_id)
                             user.get("member_ids").append(user_id)
                             return {}

    for current_channel in channels.channel_data:
        if channel_id == current_channel['channel_id']:     
            current_channel["member_ids"].append(user_id)
            
    return {}  

#Using channel_data_base, add u_id to all_owners
def channel_addowner(token, channel_id, u_id):
    '''
    When a user is added as an owner to the channel.
    '''

    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")

    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    u_id_for_token = helper_functions.check_token(token).get("u_id")
  
    #Check if they are an owner
    if helper_functions.check_uid_owner_in_channel(u_id_for_token, channel_id):
        raise error.AccessError("Authorised user not in channel or flockr owner")
    
    #If u_id already owner
    if helper_functions.check_uid_owner_in_channel(u_id, channel_id) == False:
        raise error.InputError("u_id already owner")


    #Append u_id to list of owners
    for user in channels.channel_data:
        if user.get("channel_id") == channel_id:
            user.get("owner_ids").append(u_id)
            break
     
    return {}

#Remove u_id from all_owners
def channel_removeowner(token, channel_id, u_id):
    '''
    When a user is removed as owner from the channel.
    '''
   
    #Checked invalid channel
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError("Channel not valid")

    
    # user token is invalid 
    if helper_functions.check_token(token).get('token_status'):
        raise error.InputError(description="Token invalid")

    u_id_for_token = helper_functions.check_token(token).get("u_id")
          
    #If user is an owner
    if helper_functions.check_uid_owner_in_channel(u_id_for_token, channel_id):
        raise error.AccessError("Authorised user not in channel or flockr owner")
    
    #Check if u_id is an owner. If so then remove
    u_id_not_owner = True
    for user in channels.channel_data:
        if user.get('channel_id') == channel_id:
            #check if u_id is owner
            for owner in user.get('owner_ids'):
                if owner == u_id:
                    u_id_not_owner = False
                    user['owner_ids'].remove(owner)
                    break
        if u_id_not_owner == False:
            break 
    
    if u_id_not_owner == True:
        raise error.InputError("U_id not an owner")

    return {}
