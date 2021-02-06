'''
Auth generates an account from input and allows them to access flock.

'''

import re
import hashlib
import jwt
import smtplib
from email.mime.text import MIMEText
import error
import secrets
import helper_functions

# [{u_id, email, name_first, name_last, handle_str}]
registered_users = []
registered_tokens = []
reset_codes = [] 

# for validating an Email
REGEX = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

#Secret for jwt
SECRET = 'Grape1'


def auth_login(email, password):
    '''
        Check if input matches with data
    '''
    #If email is invalid
    if not re.search(REGEX, email):
        raise error.InputError(description="Email Invalid")

    #Email does not belong to a user
    user_not_found = True
    for user in registered_users:
        if user.get('email') == email:
            u_id = user.get("u_id")
            user_not_found = False
            break

    if user_not_found:
        raise error.InputError(description="Email not registered")

    #Incorrect password booleon
    incorrect_password = True

    #Check if encrypted passwords are the same
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    for user in registered_users:
        if user.get('email') == email:
            if user.get('password') == encrypted_password:
                incorrect_password = False

    if incorrect_password:
        raise error.InputError(description="Password is invalid")

   
    #Token will be hashed u_id
    token = str(jwt.encode({'u_id' : u_id}, SECRET, algorithm='HS256'))

    verification = {'u_id': u_id,
                    'token': token,
                    }

    #See if user is already logged in
    if helper_functions.check_token(token).get('token_status') == False:
        raise error.InputError(description="User already logged in")

    #Append to registered_tokens
    registered_tokens.append(verification)
    return verification


def auth_logout(token):
    '''
        Removes the data from input from logged in data
    '''
    #Remove the user from registered_token
    invalid_token = True
    for user in registered_tokens:
        if user.get('token') == token:
            registered_tokens.remove(user)
            invalid_token = False

    if invalid_token:
        return {
            'is_success': False,
        }

    return {
        'is_success': True,
    }


def auth_register(email, password, name_first, name_last):
    '''
        Generates new data in the form of dictionary for input
    '''

    #Check if email is already taken
    if len(registered_users) == 0:
        pass
    else:
        for data in registered_users:
            if data.get("email") == email:
                raise error.InputError(description="Email is already taken")

    #If password is less then length 6
    if len(password) < 6:
        raise error.InputError(description="Password length less than 6")

    #If email invalid
    if not re.search(REGEX, email):
        raise error.InputError(description="Email Invalid")

    #If first_name is not 1 < first_name < 50
    if (len(name_first) < 1) or (len(name_first) > 50):
        raise error.InputError(description="First name less than 1 or greater than 50 characters")

    #If last_name is not 1 < last_name < 50
    if (len(name_last) < 1) or (len(name_last) > 50):
        raise error.InputError(description="Last name less than 1 or greater than 50 characters")

    #Generate a handle
    handle = name_first.lower() + name_last.lower()
    handle = handle[:20]

    #Check if handle is taken
    for user in registered_users:
        #If taken get rid of last character of handle name
        if user.get('handle') == handle:
            handle = handle[:-1]

    #Generate u_id. For now its the index of the dictionary in the list
    u_id = len(registered_users)

    #Encrypt password
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()

    #if new_user is the very first registration, make flocker owner
    permissions = 2
    if u_id == 0:
        permissions = 1
        
    new_user = {
        'email': email,
        'password': encrypted_password,
        'first_name': name_first,
        'last_name': name_last,
        'handle': handle,
        'u_id': u_id,
        'permissions': permissions,
        'profile_img_url': None
    }
    

    registered_users.append(new_user)

    #Log the user in using auth_login
    return auth_login(email, password)

def auth_passwordreset_request(email):

    # check if user is registered (existing email)
    user_not_found = True
    for user in registered_users:
        if user.get('email') == email:
            user_not_found = False
            break

    if user_not_found:
        raise error.InputError(description="Email not registered")

    # generate a reset code using secrets module (10 characters unique code)
    reset_code = secrets.token_hex(5)

    user_reset = {
        'email': email,
        'reset_code': reset_code
    }

    reset_code_new = {'reset_code': reset_code}

    # check if user has already requested and if yes, then update
    user_already_requested = False
    for user in reset_codes:
        if user.get('email') == email:
            user.update(reset_code_new)
            user_already_requested = True
            break 

    # append reset_code to list so can check later 
    if user_already_requested == False:
        reset_codes.append(user_reset)

    # send email 
    sender = 'fridaygrape1@gmail.com'
    receiver = [email]

    msg = MIMEText(reset_code)
    msg['Subject'] = 'Reset Code'
    msg['From'] = 'fridaygrape1@gmail.com'
    msg['To'] = email

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login("fridaygrape1@gmail.com", "comp1531")
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()

    return {}

def auth_passwordreset_reset(reset_code, new_password):
    # checking validity of reset code 
    invalid_code = True
    for user in reset_codes:
        # check if the code given is an existing code
        if reset_code == user.get("reset_code"):
            # grab email of user
            email = user.get("email")
            # if reset code is valid, then break out of loop
            invalid_code = False
            break

    # Raise an input error if invalid_token is true
    if invalid_code == True:
        raise error.InputError("You have entered an invalid reset code")

    # checking validity of password, if password is less then length 6
    if len(new_password) < 6:
        raise error.InputError(description="Password length less than 6")

    #Encrypt password
    encrypted_password = hashlib.sha256(new_password.encode()).hexdigest()

    # updating password 
    password_new = {'password': encrypted_password}

    for users in registered_users:
        if users['email'] == email:
            # gets rid of existing value and replaces it with new value
            users.update(password_new)
            break

    return {}
