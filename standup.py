
import auth
from datetime import datetime, timedelta
import time
import error
import threading
from channel import channel_messages
import channels
from message import message_send
import helper_functions

#{channel_id, time_finish}
STANDUPS = []

#{channel_id: [messages]}
CHANNELSMSG = {}


def helper_send_message(token, channel_id):
    '''
    Check if length has finished and then send message
    '''

    message_queue = CHANNELSMSG[channel_id]
    string = ""
    for message in message_queue:
        string += message + '\n'

    string = string.rstrip('\n')

    message_send(token, channel_id, string)

    # emove the standup from QUEUES and STANDUPS
    del CHANNELSMSG[channel_id]

    for standup in STANDUPS:
        if standup['channel_id'] == channel_id:
            STANDUPS.remove(standup)

    return

def standup_start(token, channel_id, length):
    '''
    Begin the standup
    '''
    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    

    #If channel valid
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError(description="Channel_id invalid")
    
    #If startup is active in channel
    if standup_active(token, channel_id)['is_active'] == True:
        raise error.InputError(description="Startup is currently active")
    

    #Get the time it will end
    dt_finish = datetime.now() + timedelta(seconds=length)
    time_finish = dt_finish.timestamp()

    #Append startup to STANDUPS
    STANDUPS.append({'channel_id': channel_id, 'time_finish': int(time_finish)})

    #Append to CHANNELMSGS
    CHANNELSMSG[channel_id] = []

    t = threading.Timer(int(length), helper_send_message, args=[token, channel_id])
    t.start()

    return {'time_finish': int(time_finish)}
   

def standup_active(token, channel_id):
    '''
    Check if standup is active
    '''
    # Checking is the token exist 
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    #If channel valid
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError(description="Channel_id invalid")

    #Check if standup active in channel
    is_active = False 
    time_finish = None 
    for channel in STANDUPS:
        if channel['channel_id'] == channel_id:
            is_active = True 
            time_finish = channel['time_finish']


    return {'is_active': is_active, 'time_finish': time_finish}



def standup_send(token, channel_id, message):
    '''
    Send message in standup
    '''
    # Checking is the token exist 
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    u_id = helper_functions.check_token(token).get('u_id')

    #If channel valid
    if helper_functions.check_channelid_valid(channel_id):
        raise error.InputError(description="Channel_id invalid")

    #If startup is active in channel
    if standup_active(token, channel_id)['is_active'] == False:
        raise error.InputError(description="Startup is not currently active")

    #If message is more than 1000 characters
    if len(message) > 1000:
        raise error.InputError(description="Message length too long")
            
    #Make a new message 
    for user in auth.registered_users:
        if user['u_id'] == u_id:
            handle_str = user['handle']
            break 

    string = str(handle_str) + ": " + str(message)

    #Append message to CHANNELSMSG
    CHANNELSMSG[channel_id].append(string)
    return {}

    