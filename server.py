'''
Imported files for server.
'''
import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from error import InputError

import auth
import channels
import channel
import other
import message
import user
import standup

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


#################################################################################
#                                                                               #
#                               Auth server                                     #
#                                                                               #
#################################################################################

@APP.route("/auth/register", methods=['POST'])
def auth_register():
    '''
    POST HTTP method for auth_register.
    '''
    auth_info = request.get_json()
    return_value = auth.auth_register(auth_info['email'], auth_info['password'], auth_info['name_first'], auth_info['name_last'])
    return dumps(return_value)

@APP.route("/auth/login", methods=['POST'])
def auth_login():
    '''
    POST HTTP method for auth_login.
    '''
    auth_info = request.get_json()
    return_value = auth.auth_login(auth_info['email'], auth_info['password'])
    return dumps(return_value)

@APP.route("/auth/logout", methods=['POST'])
def auth_logout():
    '''
    POST HTTP method for auth_logout.
    '''
    user_token = request.get_json()
    is_success = auth.auth_logout(user_token['token'])
    return dumps(is_success)

@APP.route("/auth/passwordreset/request", methods=['POST'])
def auth_passwordreset_request():
    '''
    POST HTTP method for auth_passwordreset_request.
    '''
    auth_info = request.get_json()
    auth.auth_passwordreset_request(auth_info['email'])
    return dumps({})

@APP.route("/auth/passwordreset/reset", methods=['POST'])
def auth_passwordreset_reset():
    '''
    POST HTTP method for auth_passwordreset_reset.
    '''
    auth_info = request.get_json()
    auth.auth_passwordreset_reset(auth_info['reset_code'], auth_info['new_password'])
    return dumps({})

#################################################################################
#                                                                               #
#                             Channels server                                   #
#                                                                               #
#################################################################################

@APP.route("/channels/create", methods=['POST'])
def channels_create():
    '''
    POST HTTP method for channels_create.
    '''
    channels_info = request.get_json()
    return_value = channels.channels_create(channels_info['token'], channels_info['name'], channels_info['is_public'])
    return dumps(return_value)

@APP.route("/channels/list", methods=['GET'])
def channels_list():
    '''
    GET HTTP method for channels_list.
    '''
    token = request.args.get('token')
    return_value = channels.channels_list(token)
    return dumps(return_value)

@APP.route("/channels/listall", methods=['GET'])
def channels_listall():
    '''
    GET HTTP method for channels_listall.
    '''
    token = request.args.get('token')
    return_value = channels.channels_listall(token)
    return dumps(return_value)

#################################################################################
#                                                                               #
#                             Channel server                                    #
#                                                                               #
#################################################################################

@APP.route("/channel/invite", methods=['POST'])
def channel_invite():
    '''
    POST HTTP method for channel_invite.
    '''
    channel_info = request.get_json()
    channel.channel_invite(channel_info['token'], channel_info['channel_id'], channel_info['u_id'])
    return dumps({})

@APP.route("/channel/details", methods=['GET'])
def channel_details():
    '''
    GET HTTP method for channel_details.
    '''
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    return_value = channel.channel_details(token, int(channel_id))
    return dumps(return_value)

@APP.route("/channel/leave", methods=['POST'])
def channel_leave():
    '''
    POST HTTP method for channel_leave.
    '''
    channel_info = request.get_json()
    channel.channel_leave(channel_info['token'], int(channel_info['channel_id']))
    return dumps({})

@APP.route("/channel/join", methods=['POST'])
def channel_join():
    '''
    POST HTTP method for channel_join.
    '''
    channel_info = request.get_json()
    channel.channel_join(channel_info['token'], int(channel_info['channel_id']))
    return dumps({})

@APP.route("/channel/addowner", methods=['POST'])
def channel_addowner():
    '''
    POST HTTP method for channel_addowner.
    '''
    channel_info = request.get_json()
    channel.channel_addowner(channel_info['token'], int(channel_info['channel_id']), int(channel_info['u_id']))
    return dumps({})

@APP.route("/channel/removeowner", methods=['POST'])
def channel_removeowner():
    '''
    POST HTTP method for channel_removeowner.
    '''
    remove_owner = request.get_json()
    channel.channel_removeowner(remove_owner['token'], int(remove_owner['channel_id']), int(remove_owner['u_id']))
    return dumps({})
   
@APP.route("/channel/messages", methods=['GET'])
def channel_messages():
    '''
    GET HTTP method for channel_messages.
    '''
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    return_value = channel.channel_messages(token, int(channel_id), int(start))
    return dumps(return_value)

#################################################################################
#                                                                               #
#                             User server                                       #
#                                                                               #
#################################################################################

@APP.route("/user/profile", methods=['GET'])
def user_profile():
    '''
    GET HTTP method for user_profile.
    '''
    token = request.args.get('token')
    u_id = request.args.get('u_id')
    u_id = int(u_id)
    profile = user.user_profile(token, u_id)
    return dumps(profile)

@APP.route("/user/profile/setemail", methods=['PUT'])
def user_profile_setemail():
    '''
    PUT HTTP method for user_profile_setemail.
    '''
    user_data = request.get_json()
    user.user_profile_setemail(user_data['token'], user_data['email'])
    return dumps({})

@APP.route("/user/profile/sethandle", methods=['PUT'])
def user_profile_sethandle():
    '''
    PUT HTTP method for user_profile_sethandle.
    '''
    user_data = request.get_json()
    user.user_profile_sethandle(user_data['token'], user_data['handle_str'])
    return dumps({})

@APP.route("/user/profile/uploadphoto", methods=['POST'])
def user_profile_uploadphoto():
    '''
    PUT HTTP method for user_profile_upload.
    '''
    user_data = request.get_json()
    user.user_profile_uploadphoto(user_data['token'], user_data['img_url'], int(user_data['x_start']), int(user_data['y_start']), int(user_data['x_end']), int(user_data['y_end']))
    return dumps({})

@APP.route("/static/<filename>", methods=['GET'])
def user_profile_image(filename):
    """
    Route that serves profile images
    """
    return send_from_directory('static', filename)

@APP.route("/user/profile/setname", methods=['PUT'])
def user_profile_setname():
    '''
    PUT HTTP method for user_profile_setname.
    '''
    user_data = request.get_json()
    user.user_profile_setname(user_data['token'], user_data['name_first'], user_data['name_last'])
    return dumps({})

#################################################################################
#                                                                               #
#                             Message server                                    #
#                                                                               #
#################################################################################

@APP.route("/message/send", methods=['POST'])
def message_send():
    '''
    POST HTTP method for message_send.
    '''
    message_info = request.get_json()
    message_return = message.message_send(message_info['token'], int(message_info['channel_id']), message_info['message'])
    return dumps(message_return)

@APP.route("/message/remove", methods=['DELETE'])
def message_remove():
    '''
    DELETE HTTP method for message_remove.
    '''
    message_info = request.get_json()
    message.message_remove(message_info['token'], int(message_info['message_id']))
    return dumps({})

@APP.route("/message/edit", methods=['PUT'])
def message_edit():
    '''
    PUT HTTP method for message_edit.
    '''
    message_info = request.get_json()
    message.message_edit(message_info['token'], int(message_info['message_id']), message_info['message'])
    return dumps({})

@APP.route("/message/sendlater", methods=['POST'])
def message_sendlater():
    '''
    PUT HTTP method for message_sendlater.
    '''
    message_info = request.get_json()
    message_return = message.message_sendlater(message_info['token'], int(message_info['channel_id']), message_info['message'], int(message_info['time_sent']))
    return dumps(message_return)

@APP.route("/message/react", methods=['POST'])
def message_react():
    '''
    POST HTTP method for message_react.
    '''
    message_info = request.get_json()
    message.message_react(message_info['token'], int(message_info['message_id']), int(message_info['react_id']))
    return dumps({})

@APP.route("/message/unreact", methods=['POST'])
def message_unreact():
    '''
    POST HTTP method for message_unreact.
    '''
    message_info = request.get_json()
    message.message_unreact(message_info['token'], int(message_info['message_id']), int(message_info['react_id']))
    return dumps({})

@APP.route("/message/pin", methods=['POST'])
def message_pin():
    '''
    POST HTTP method for message_pin
    '''
    message_info = request.get_json()
    message.message_pin(message_info['token'], int(message_info['message_id']))
    return dumps({})
    
@APP.route("/message/unpin", methods=['POST'])
def message_unpin():
    '''
    POST HTTP method for message_unpin
    '''
    message_info = request.get_json()
    message.message_unpin(message_info['token'], int(message_info['message_id']))
    return dumps({}) 
        
#################################################################################
#                                                                               #
#                             Other server                                      #
#                                                                               #
#################################################################################

@APP.route("/clear", methods=['DELETE'])
def clear():
    '''
    DELETE HTTP method for clear.
    '''
    other.clear()
    return dumps({})

@APP.route("/users/all", methods=['GET'])
def users_all():
    '''
    GET HTTP method for users_all.
    '''
    token = request.args.get('token')
    return_value = other.users_all(token)
    return dumps(return_value)

@APP.route("/search", methods=['GET'])
def search():
    '''
    GET HTTP method for search.
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return_value = other.search(token, query_str)
    return dumps(return_value)

@APP.route("/admin/userpermission/change", methods=['POST'])
def admin_userpermission_change():
    '''
    POST HTTP method for admin_userpermission_change.
    '''
    admin_info = request.get_json()
    other.admin_userpermission_change(admin_info['token'], int(admin_info['u_id']), int(admin_info['permission_id']))
    return dumps({})

#################################################################################
#                                                                               #
#                             Standup server                                    #
#                                                                               #
#################################################################################

@APP.route("/standup/start", methods =['POST'])
def standup_start():
    '''
    POST HTTP method for standup_start
    '''
    payload = request.get_json()
    return_value = standup.standup_start(payload['token'], int(payload['channel_id']), int(payload['length']))
    return dumps(return_value)

@APP.route("/standup/active", methods =['GET'])
def standup_active():
    '''
    POST HTTP method for standup_active
    '''
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    return_value = standup.standup_active(token, int(channel_id))
    return dumps(return_value)

@APP.route("/standup/send", methods =['POST'])
def standup_send():
    '''
    POST HTTP method for standup_send
    '''
    payload = request.get_json()
    return_value = standup.standup_send(payload['token'], int(payload['channel_id']), payload['message'])
    return dumps(return_value)


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
