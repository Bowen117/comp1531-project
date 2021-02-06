'''
Imported files for user.
'''
import re
import error
import auth
from PIL import Image
import urllib
from flask import url_for
import os
import helper_functions

def user_profile(token, u_id):
    '''
    Returns profile details for a valid user.
    '''
    # Test for an invalid token 
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    # Testing for an invalid u_id
    if helper_functions.check_uid_valid(u_id):
        raise error.InputError("You have entered an invalid user id")
    
    # Getting all the user details 
    for users in auth.registered_users:
        if users['u_id'] == u_id and users.get('profile_img_url') == None:
            user_detail = {
                'user' : {
                    'u_id': users.get('u_id'),
                    'email': users.get('email'),
                    'name_first': users.get('first_name'),
                    'name_last': users.get('last_name'),
                    'handle_str': users.get('handle'),
                }
            }
        if users['u_id'] == u_id and users.get('profile_img_url') != None:
            user_detail = {
                'user' : {
                    'u_id': users.get('u_id'),
                    'email': users.get('email'),
                    'name_first': users.get('first_name'),
                    'name_last': users.get('last_name'),
                    'handle_str': users.get('handle'),
                    'profile_img_url': users.get('profile_img_url')
                }
            }
            break

    return user_detail

def user_profile_setname(token, name_first, name_last):
    '''
    Updates the authorised user's first and last name.
    '''
    
    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    user_id = helper_functions.check_token(token).get('u_id')

    #If first_name is not 1 < first_name < 50
    if (len(name_first) < 1) or (len(name_first) > 50):
        raise error.InputError("First name invalid, needs to be between 1 and 50 characters")

    #If last_name is not 1 < last_name < 50
    if (len(name_last) < 1) or (len(name_last) > 50):
        raise error.InputError("Last name invalid, needs to be between 1 and 50 characters")

    # new value for keys to update name
    new_name = {'first_name': name_first, 'last_name': name_last}

    # loops through users in list
    for users in auth.registered_users:
        if users['u_id'] == user_id:
            # gets rid of existing value and replaces it with new value
            users.update(new_name)
            break

    return {}

def user_profile_setemail(token, email):
    '''
    Updates the authorised user's email.
    '''
    #Use regex to check if email is valid
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    u_id = helper_functions.check_token(token).get('u_id')

    # Testing for an invalid email
    invalid_email = False
    for user in auth.registered_tokens:
        if user.get("email") == email:
            invalid_email = True 
            break
        
    if invalid_email:
        raise error.InputError("You have entered an invalid email")

    #If email is invalid
    if not re.search(regex, str(email)):
        raise error.InputError(description="Email Invalid")
    
    # Testing for email that is already being used
    for data in auth.registered_users:
        if data.get('email') == email:
            raise error.InputError("Email is already being used")
            
    # Updating the user's email
    for users in auth.registered_users:
        if users.get('u_id') == u_id:
            users['email'] = email
            break
        
    return {}

def user_profile_sethandle(token, handle_str):
    '''
    Update the authorised user's handle.
    '''
    #Check if token valid and get u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    u_id = helper_functions.check_token(token).get('u_id')
    
    #If handle_str valid
    if len(handle_str) < 3 or len(handle_str) > 20:
        raise error.InputError(description="Handle_str invalid")

    #If handle_str already being used
    for item in auth.registered_users:
        if item.get("handle") == handle_str:
            raise error.InputError(description="Handle_str being used")
    
    #Update handle_str
    for item in auth.registered_users:
        if item.get("u_id") == u_id:
            item["handle"] = handle_str
            break

    return {}

def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    '''
    Update the authorised user's profile.
    '''
    # Checking is the token exist then getting their u_id
    if helper_functions.check_token(token).get('token_status'):
        raise error.AccessError(description="Token invalid")
    
    u_id = helper_functions.check_token(token).get('u_id')
    
    try:
        urllib.request.urlretrieve(img_url, f"src/static/{u_id}.jpg")
    except:
        raise error.InputError(description="Url can not be opened")
    
    opened_img = Image.open(f"src/static/{u_id}.jpg")
    
    if opened_img.format != "JPEG":
        raise error.InputError(description="The image is not JPEG type")
    
    width, height = opened_img.size

    if x_start < 0 or y_start < 0 or x_end > width or y_end > height:
        raise error.InputError(description="The crop bound is greater than the orginal photo.")
    
    
    new_image = opened_img.crop((x_start, y_start, x_end, y_end)) 
    new_image.save(f"src/static/{u_id}.jpg")

    profile_img_url = url_for('static', filename=f'{u_id}.jpg', _external=True)

    for users in auth.registered_users:
        if users['u_id'] == u_id:
            users['profile_img_url'] = profile_img_url
            break

    return {}
