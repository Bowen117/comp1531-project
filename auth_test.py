
'''
Imported files for auth_test.
'''
import pytest 
import error 
import auth
from other import clear
from user import user_profile


#################################################################################
#                                                                               #
#                      auth_login testing functions                             #
#                                                                               #
#################################################################################

def test_login_wrong_password():
    '''
    Testing when the wrong password is used to login.
    '''
    current_user = auth.auth_register("test1@gmail.com", "password", "Firstname", "Lastname")
    auth.auth_logout(current_user.get("token"))
    
    with pytest.raises(error.InputError):
        auth.auth_login("test1@gmail.com", "wrongpassword")

    clear()

def test_login_unregistered_email():
    '''
    Testing when email is unregistered.
    '''
    with pytest.raises(error.InputError):
        auth.auth_login("unregistered_email@gmail.com", "password")
    
    clear()

def test_login_already_logged_in():
    ''' 
    Testing when user tries to login although they are already logged in.
    '''
    auth.auth_register("test2@gmail.com", "password", "Firstname", "Lastname")

    with pytest.raises(error.InputError):
        auth.auth_login("test2@gmail.com", "password")
    
    clear()

def test_login_valid():
    '''
    Testing if user is able to login successfully.
    '''
    current_user = auth.auth_register("test3@gmail.com", "password", "Firstname", "Lastname")
    user_detail = user_profile(current_user.get("token"), current_user.get("u_id"))
    assert user_detail.get('user').get('email') == "test3@gmail.com"
    assert user_detail.get('user').get('name_first') == "Firstname"
    assert user_detail.get('user').get('name_last') == "Lastname"

    auth.auth_logout(current_user.get("token"))
    auth.auth_login("test3@gmail.com", "password")
    assert user_detail.get('user').get('email') == "test3@gmail.com"
    assert user_detail.get('user').get('name_first') == "Firstname"
    assert user_detail.get('user').get('name_last') == "Lastname"

def test_login_invaild_email():
    '''
    Testing when an invalid email is used to login.
    '''
    with pytest.raises(error.InputError):
        auth.auth_login("wrong_format_email.com", "password")

#################################################################################
#                                                                               #
#                      auth_logout testing functions                            #
#                                                                               #
#################################################################################

def test_valid_logout_token():
    '''
    Testing when a valid token is used to logout.
    '''
    clear()
    current_user = auth.auth_register("test4@gmail.com", "password", "Firstname", "Lastname")
    assert auth.auth_logout(current_user.get('token')).get('is_success') == True
    
def test_valid_logout_error():
    '''
    Testing when there is a logout error.
    '''
    clear()
    current_user = auth.auth_register("test5@gmail.com", "password", "Firstname", "Lastname")
    assert auth.auth_logout(current_user.get('token')).get('is_success') == True

def test_invalid_logout():
    '''
    Testing when logout is invalid.
    '''
    clear()
    assert auth.auth_logout('invalid_token_not_exist').get('is_success') == False

def test_invalid_logout_with_registered_user():
    '''
    Testing when logout is invalid.
    '''
    clear()
    auth.auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    assert auth.auth_logout('invalid_token').get('is_success') == False

#################################################################################
#                                                                               #
#                      auth_register testing functions                          #
#                                                                               #
#################################################################################

def test_valid_register():
    '''
    Testing if auth_register works.
    '''
    clear()
    current_user = auth.auth_register("testregister@gmail.com", "password", "Firstname", "Lastname")
    user_detail = user_profile(current_user.get("token"), current_user.get("u_id"))
    assert user_detail.get('user').get('email') == "testregister@gmail.com"
    assert user_detail.get('user').get('name_first') == "Firstname"
    assert user_detail.get('user').get('name_last') == "Lastname"
  
    current_user = auth.auth_register("test2@domain.org", "password", "Firstname", "Lastname")
    user_detail = user_profile(current_user.get("token"), current_user.get("u_id"))
    assert user_detail.get('user').get('email') == "test2@domain.org"
    assert user_detail.get('user').get('name_first') == "Firstname"
    assert user_detail.get('user').get('name_last') == "Lastname"

def test_invalid_register():
    '''
    Testing when register is invalid.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test#gmail.com", "password", "Firstname", "Lastname")

def test_email_already_taken():
    '''
    Testing when the email being registered has already been taken.
    ''' 
    clear()
    auth.auth_register("smiths@gmail.com", "password", "John", "Smith")
    
    with pytest.raises(error.InputError):
        auth.auth_register("smiths@gmail.com", "second_password", "James", "Smith")

def test_invalid_email_format_no_domain():
    '''
    Testing when the email format is invalid bc of no domain.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@.com", "password", "Firstname", "Lastname")

def test_invalid_email_format_no_user_id():
    '''
    Testing when the email format is invalid bc of no 'username' for the email.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("@gmailcom", "password", "Firstname", "Lastname")

def test_invalid_email_format():
    '''
    Testing when the email has an invalid format.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("testgmail.com", "password", "Firstname", "Lastname")

def test_invalid_emaildomain():
    '''
    Testing when the email domain is invalid.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@com", "password", "Firstname", "Lastname")
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail", "password", "Firstname", "Lastname")
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmailcom", "password", "Firstname", "Lastname")
    with pytest.raises(error.InputError):
        auth.auth_register("test@.", "password", "Firstname", "Lastname")

def test_register_no_password():
    '''
    Testing when there is no password being registered.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail.com", "", "Firstname", "Lastname")

def test_password_less_than_six():
    '''
    Testing when password is less than 6 characters.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail.com", "pass", "Firstname", "Lastname")

def test_valid_password():
    '''
    Testing if the password being used to register is valid.
    '''
    clear()
    current_user = auth.auth_register("testpassword@gmail.com", "password", "Firstname", "Lastname")
    user_detail = user_profile(current_user.get("token"), current_user.get("u_id"))
    assert user_detail.get('user').get('name_last') == "Lastname" 

def test_no_first_name():
    '''
    Testing when there isn't a first name being registered.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail.com", "password", "", "Lastname")

def test_first_name_too_long():
    '''
    Testing when the first name entered is too long.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail.com", "password", "nametooooooooooooooooooooooooooooooooooooooooooooooooooooooolong", "Lastname")

def test_valid_first_name():
    '''
    Testing when a valid first name is registered.
    '''
    clear()
    current_user = auth.auth_register("testfirst@gmail.com", "password", "first-name", "Lastname")
    details = user_profile(current_user.get("token"), current_user.get("u_id"))
    
    assert details.get('user').get('name_first') == "first-name"

def test_no_last_name():
    '''
    Testing when there is no last name being registered.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail.com", "password", "Firstname", "")

def test_last_name_too_long():
    '''
    Testing when the last name is too long.
    '''
    clear()
    with pytest.raises(error.InputError):
        auth.auth_register("test@gmail.com", "password", "Firstname", "lastnametooooooooooooooooooooooooooooooooooooooooooooooooooooooolong")

def test_valid_last_name():
    '''
    Testing when the last name being registered is valid.
    '''
    clear()
    current_user = auth.auth_register("testvalidlast@gmail.com", "password", "Firstname", "Lastname")
    user_details = user_profile(current_user.get("token"), current_user.get("u_id"))

    assert user_details.get('user').get('name_last') == "Lastname"

def test_no_handle():
    '''
    Testing when there isn't a handle.
    '''
    clear()
    with pytest.raises(error.InputError):
        assert auth.auth_register("test@gmail.com", "password", "Firstname", "")

def test_handle_too_long():
    '''
    Testing when the handle is too long.
    '''
    clear()
    with pytest.raises(error.InputError):
        assert auth.auth_register("test@gmail.com", "password",
                                  "Firstname", "lastnametooooooooooooooooooooooooooooooooooooooooooooooooooooooolong")

def test_invalid_handle():
    '''
    Testing when the handle is invalid.
    '''
    clear()
    with pytest.raises(error.InputError):
        assert auth.auth_register(
            "test@gmail.com", "password", "Firstname", "")

def test_valid_handle():
    '''
    Testing if the handle is valid and working.
    '''
    clear()
    current_user = auth.auth_register("test@gmail.com", "password", "Firstname", "Lastname")
    user_detail = user_profile(current_user.get("token"), current_user.get("u_id"))

    assert user_detail.get('user').get('name_last') == "Lastname"

#################################################################################
#                                                                               #
#                auth_passwordreset_request testing functions                   #
#                                                                               #
#################################################################################
def test_unregistered_user(): 
    clear()
    with pytest.raises(error.InputError):
        auth.auth_passwordreset_request("unregistered@gmail.com")

def test_working_request():
    clear()
    user_1 = auth.auth_register("fridaygrape1@gmail.com", "password", "First", "Last")
    auth.auth_passwordreset_request("fridaygrape1@gmail.com")
    code = auth.reset_codes[0].get('reset_code')
    auth.auth_passwordreset_reset(code, "newpassword")
    auth.auth_logout(user_1.get("token"))
    auth.auth_login("fridaygrape1@gmail.com", "newpassword")

#################################################################################
#                                                                               #
#                 auth_passwordreset_reset testing functions                    #
#                                                                               #
#################################################################################

def test_invalid_resetcode():
    clear()
    auth.auth_register("fridaygrape1@gmail.com", "password", "First", "Last")
    invalid_code = 123213
    with pytest.raises(error.InputError):
        auth.auth_passwordreset_reset(invalid_code, "newpassword")

def test_invalid_password():
    clear()
    auth.auth_register("fridaygrape1@gmail.com", "password", "First", "Last")
    auth.auth_passwordreset_request("fridaygrape1@gmail.com")
    code = auth.reset_codes[0].get('reset_code')
    with pytest.raises(error.InputError):
        auth.auth_passwordreset_reset(code, "lol")

def test_working_reset():
    clear()
    user_1 = auth.auth_register("fridaygrape1@gmail.com", "password", "First", "Last")
    auth.auth_passwordreset_request("fridaygrape1@gmail.com")
    code = auth.reset_codes[0].get('reset_code')
    auth.auth_passwordreset_reset(code, "newpassword")
    auth.auth_logout(user_1.get("token"))
    auth.auth_login("fridaygrape1@gmail.com", "newpassword")

def test_working_reset_twice():
    clear()
    user_1 = auth.auth_register("fridaygrape1@gmail.com", "password", "First", "Last")
    auth.auth_passwordreset_request("fridaygrape1@gmail.com")
    code = auth.reset_codes[0].get('reset_code')
    auth.auth_passwordreset_reset(code, "newpassword")
    auth.auth_logout(user_1.get("token"))
    auth.auth_login("fridaygrape1@gmail.com", "newpassword")

    auth.auth_passwordreset_request("fridaygrape1@gmail.com")
    code = auth.reset_codes[0].get('reset_code')
    auth.auth_passwordreset_reset(code, "newerpassword")
    auth.auth_logout(user_1.get("token"))
    auth.auth_login("fridaygrape1@gmail.com", "newerpassword")

def test_working_multiple_users():
    clear()
    user_1 = auth.auth_register("fridaygrape1@gmail.com", "password", "First", "Last")
    auth.auth_passwordreset_request("fridaygrape1@gmail.com")
    code = auth.reset_codes[0].get('reset_code')
    auth.auth_passwordreset_reset(code, "newpassword")
    auth.auth_logout(user_1.get("token"))
    auth.auth_login("fridaygrape1@gmail.com", "newpassword")

    user_2 = auth.auth_register("pomeranians37@gmail.com", "password", "First", "Last")
    auth.auth_passwordreset_request("pomeranians37@gmail.com")
    code = auth.reset_codes[1].get('reset_code')
    auth.auth_passwordreset_reset(code, "newpassword")
    auth.auth_logout(user_2.get("token"))
    auth.auth_login("pomeranians37@gmail.com", "newpassword")
