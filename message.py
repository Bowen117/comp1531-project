'''
Imported files for message.
'''
import time
from datetime import datetime
import auth
import error 
import channels
import hangman
import helper_functions

# list of generated message ids:
message_ids = []


def message_send(token, channel_id, message):
    '''
    Grabbing a message and sending it.
    '''
    if len(message) > 1000:
        raise error.InputError("Messages can't have more than 1000 characters")

    #Check token valid
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")

    user_id = helper_functions.check_token(token).get('u_id')
  
    invalid_channel_id = True
    not_in_channel = True
    # Checking is the token exist then getting their u_id
    for channel_datas in channels.channel_data:
        if channel_datas.get("channel_id") == channel_id:
            invalid_channel_id = False
            if user_id in channel_datas['member_ids']:
                not_in_channel = False

    # If token is invalid return an error
    if invalid_channel_id:
        raise error.AccessError("You have entered an invalid channel id.")

    if not_in_channel:
        raise error.AccessError("You are not in this channel.")
    
    time_create_date = datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()

    # Generate message ID
    gen_id = len(message_ids) + 1
    message_id = {
        'message_id': gen_id,
    }

    react_info = [{
        'react_id': 1,
        'u_ids': [],
    }]

    msg = {
        'message_sent': message,
        'message_id': gen_id,
        'user_id': user_id,
        'time_created': time_create,
        'reacts': react_info,
        'is_pinned': False
    }

    message_ids.append(message_id)

    for channels_data in channels.channel_data:
        if channels_data.get('channel_id') == channel_id:
            channels_data['messages'].append(msg)

    
    # Hang man option
    if "/hangman" in message:
        hangman.start_hangman(token, channel_id)
    if "/guess" in message:
        hangman.hangman_guess(token, channel_id, message[7])
    if "/stop" in message:
        hangman.hangman_stop(token, channel_id) 
    if "/reveal" == message:
        hangman.hangman_reveal(token, channel_id) 
        

    return message_id

def message_remove(token, message_id):
    '''
    Removing a message that is requested by the user.
    '''
    #If token invalid
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    user_id = helper_functions.check_token(token).get('u_id')

    # Checking if message ID is valid
    invalid_m_id = True
    for data in channels.channel_data:
        for msg in data['messages']:
            if msg.get('message_id') == message_id:
                channel_id = data.get('channel_id')
                invalid_m_id = False
                break

    if invalid_m_id:
        raise error.InputError("You have entered an invalid message ID")
    
    
    #Check if message is from the authorised user
    # Go inside message to check if message_id is the same in order to remove the message
    # Return error if message no longer existing
    for data in channels.channel_data:
        for message_data in data.get('messages'):
            if message_data.get('message_id') == message_id:
                #check if owner
                if helper_functions.check_uid_owner_in_channel(user_id, channel_id):
                        if message_data.get('user_id') != user_id:
                            raise error.AccessError("Not an owner or not user who sent msg")

                if msg['message_sent'] == None: 
                    raise error.InputError("Message no longer exists")
                else:
                    data.get('messages').remove(message_data)
                break
    return {}

def message_edit(token, message_id, message):
    '''
    Given a message id and user token edit the message.
    '''
    #Token invalid check
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    user_id = helper_functions.check_token(token).get('u_id')

    # Error message too long
    if len(message) > 1000:
        raise error.InputError("You have message longer than 1000 words")

    invalid_messages_id = True

    # Testing if the message id is valid
    for data in channels.channel_data:
        for msg in data['messages']:
            if msg.get('message_id') == message_id:
                channel_id = data.get("channel_id")
                invalid_messages_id = False
    
    # Raising the error
    if invalid_messages_id:
        raise error.InputError("You have entered an invalid message id")


    # Editing the message
    for data in channels.channel_data:
        for message_data in data.get('messages'):
            if message_data.get("message_id") == message_id:
                #check if owner
                if helper_functions.check_uid_owner_in_channel(user_id, channel_id):
                        if message_data.get('user_id') != user_id:
                            raise error.AccessError("Not an owner or not user who sent msg")
                    
                message_data['message_sent'] = message
                break
    return {}

def message_sendlater(token, channel_id, message, time_sent):
    '''
    Given a message and user token send the message later.
    '''
    #Token invalid test
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    user_id = helper_functions.check_token(token).get('u_id')
    if len(message) > 1000:
        raise error.InputError("You have message longer than 1000 words")

    if message == '':
        raise error.InputError("no messages")
    
    invalid_channel_id = True
    not_in_channel = True
    # Checking is the token exist then getting their u_id
    for channel_datas in channels.channel_data:
        if channel_datas.get("channel_id") == channel_id:
            invalid_channel_id = False
            if user_id in channel_datas['member_ids']:
                not_in_channel = False

    if invalid_channel_id:
        raise error.InputError("You have entered an invalid channel id.")

    if not_in_channel:
        raise error.AccessError("You are not in this channel.")

    time_create_date = datetime.now().replace(microsecond=0)
    time_create = time_create_date.timestamp()
     
    if time_sent < time_create:
        raise error.InputError("Can not send message to that time.")
    time_to_be_sent = time_sent - time_create
    time.sleep(time_to_be_sent) 
    
    return message_send(token, channel_id, message)
    
def message_react(token, message_id, react_id):
    '''
    Given a message, allow the user to add a react to it.
    '''
    # Takes in react_id as a param --> need to be generated when the message is sent

    # Checking if token is valid
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    user_id = helper_functions.check_token(token).get('u_id')

    # Checking if message ID is valid
    invalid_m_id = True
    for data in channels.channel_data:
        for msg in data['messages']:
            if msg.get('message_id') == message_id:
                #channel_id = data.get('channel_id')
                invalid_m_id = False
                break
        
    if invalid_m_id:
        raise error.InputError('You have entered an invalid message ID')
    
    for user in auth.registered_tokens:
        if user.get("token") == token:
            user_id = user.get('u_id')
            break

    already_reacted = True

    if react_id != 1:
        raise error.InputError('Invalid react_id entered')

    for data in channels.channel_data:
        for message_data in data.get('messages'):
            if message_id == message_data.get('message_id'):
                for react_data in message_data.get('reacts'):
                    if react_id == 1:
                        if user_id not in react_data['u_ids']:
                            react_data['u_ids'].append(user_id) 
                            already_reacted = False 
                            break
                          
    if already_reacted:
        raise error.InputError('You have already reacted to this message')

    return {}

def message_unreact(token, message_id, react_id):
    '''
    Given a message, allow the user to unreact.
    '''
    # Checking if token is valid
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    user_id = helper_functions.check_token(token).get('u_id')

    # Checking if message ID is valid
    invalid_m_id = True
    for data in channels.channel_data:
        for msg in data['messages']:
            if msg.get('message_id') == message_id:
                #channel_id = data.get('channel_id')
                invalid_m_id = False
                break
        
    if invalid_m_id:
        raise error.InputError('You have entered an invalid message ID')

    for user in auth.registered_tokens:
        if user.get("token") == token:
            user_id = user.get('u_id')
            break

    already_unreacted = True

    if react_id != 1:
        raise error.InputError('Invalid react_id entered')

    for data in channels.channel_data:
        for message_data in data.get('messages'):
            if message_id == message_data.get('message_id'):
                for react_data in message_data.get('reacts'):
                    if react_id == 1:
                        if user_id in react_data['u_ids']:
                            react_data['u_ids'].remove(user_id) 
                            already_unreacted = False 
                            break
                
    if already_unreacted:
        raise error.InputError('You have already unreacted this message')

    return {}

def message_pin(token, message_id):
    # check input error 
    #   message_id invalid:

    #Invalid token test
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")

    user_id = helper_functions.check_token(token).get('u_id')

    channel_id = ""
    invalid_msg_id = True
    for data in channels.channel_data:
        for msg in data['messages']:
            if msg.get('message_id') == message_id:
                channel_id = int(data.get('channel_id'))
                invalid_msg_id = False
                break

    if invalid_msg_id == True:
        raise error.InputError("You have entered an invalid message ID")
          
    #   not owner / flockr owner
    
    for channel_datas in channels.channel_data:
        if channel_datas.get("channel_id") == channel_id:
            if user_id not in channel_datas['owner_ids']:
                raise error.AccessError("You are not in this channel / not an owner")
            else: 
                 break

    # message already pinned? if not, pin.
    for data in channels.channel_data:
        for message_data in data.get('messages'):
            if message_data.get("message_id") == message_id:
                if message_data.get("is_pinned") == True:
                    raise error.InputError("This message is already pinned")
                else:
                    message_data['is_pinned'] = True
          
    return {}   

def message_unpin(token, message_id):
    # check input error 
    #   message_id invalid:

    #Invalid token test
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    user_id = helper_functions.check_token(token).get('u_id')

    channel_id = ""
    invalid_msg_id = True
    for data in channels.channel_data:
        for msg in data['messages']:
            if msg.get('message_id') == message_id:
                channel_id = int(data.get('channel_id'))
                invalid_msg_id = False
                break

    if invalid_msg_id:
        raise error.InputError("You have entered an invalid message ID")
          
    # check access error
    #   not member of channel
    user_id = ""
    for user in auth.registered_tokens:
        if user.get("token") == token:
            user_id = int(user.get('u_id'))
            break

    #   not owner / flockr owner
    for channel_datas in channels.channel_data:
        if channel_datas.get("channel_id") == channel_id:
            if user_id not in channel_datas['owner_ids']:
                raise error.AccessError("You are not in this channel / not an owner")
            else: 
                break

    # message already pinned? if not, pin.
    for data in channels.channel_data:
        for message_data in data.get('messages'):
            if message_data.get("message_id") == message_id:
                if message_data.get("is_pinned") == False:
                    raise error.InputError("This message is already unpinned")
                else:
                    message_data['is_pinned'] = False
          
    return {}

    
