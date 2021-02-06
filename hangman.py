'''
Imported files for Hangman.
'''
import channel
import channels
import auth 
import message
import auth
import channel
import channels 
import message
import error 
from flask import url_for
import random
from english_words import english_words_lower_set

HANGMAN = []
BOT_TOKEN = 'bottokenforhangman'
def check_exsisting_hangman(channel_id): #pragma: no cover
    '''
    Check pre-exisiting game
    '''
    game_exist = False
    for curr_game in HANGMAN:
        if curr_game['channel_id'] == channel_id:
            game_exist = True
            break

    return game_exist

def check_nonexsisting_hangman(channel_id): #pragma: no cover
    '''
    Check no game
    '''
    game_nonexist = True
    for curr_game in HANGMAN:
        if curr_game['channel_id'] == channel_id:
            game_nonexist = False
            break

    return game_nonexist

def helper_token_valid(token): #pragma: no cover
    '''
    Check token valid
    '''
    token_invalid = True
    for user in auth.registered_tokens:
        if user.get('token') == token:
            token_invalid = False 
            break 

    return token_invalid

def helper_channel_valid(channel_id): #pragma: no cover
    '''
    Check channel_id valid
    '''
    channel_invalid = True 
    for channel in channels.channel_data:
        if channel['channel_id'] == channel_id:
            channel_invalid = False 
            break 

    return channel_invalid

def register_bot(): #pragma: no cover
    """
    Create a bot to run the hangman 
    """
    profile_img_url = url_for('static', filename='bot.jpg', _external=True)
    user = {'u_id': -1,
            'email': "hangman_bot@gmail.com",
            'first_name': "Hangman",
            'last_name': "Bot",
            'handle': "hangmanbot",
            'profile_img_url': profile_img_url
            }
    user2 = {'u_id': -1,
             'token': BOT_TOKEN
    }
    auth.registered_users.append(user)
    auth.registered_tokens.append(user2)
            
def calling_bot_to_channel(channel_id): #pragma: no cover
    not_in_channel = True
    for user in auth.registered_tokens:
        if user.get('u_id') == -1:
            not_in_channel = False 
            break 
    if not_in_channel:
        register_bot()

    for channel_ids in channels.channel_data:
        if channel_id == channel_ids['channel_id']:
            for ids in channel_ids['member_ids']:
                if ids != -1:
                    channel.channel_join(BOT_TOKEN, channel_id)

def start_hangman(token, channel_id): #pragma: no cover
    """
    start the hangman game
    """
    # Testing 
    #If token valid
    if helper_token_valid(token):
        raise error.InputError(description="Invalid token")

    #If channel valid
    if helper_channel_valid(channel_id):
        raise error.InputError(description="Channel_id invalid")
    
    # Checking for a game 
    if check_exsisting_hangman(channel_id):
        raise error.InputError(description="There is already a hangman game in this channel")


    word = random.choice(tuple(english_words_lower_set))

    # Initialising the game data 
    hangman_game = {
        'channel_id': channel_id,
        'word': word,
        'state': word,
        'num_guess': 0,
        'char_guess': []
    }
    HANGMAN.append(hangman_game)

    calling_bot_to_channel(channel_id)
    message_hangman = r"Hangman has started! *\(^v^)/*"
    message.message_send(BOT_TOKEN, channel_id, message_hangman) 

    return hangman_state_initialise(hangman_game, channel_id)

def hangman_guess(token, channel_id, character): #pragma: no cover
    """
    Guess a letter
    """
    #If token valid
    if helper_token_valid(token):
        raise error.InputError(description="Invalid token")

    #If channel valid
    if helper_channel_valid(channel_id):
        raise error.AccessError(description="Channel_id invalid")
    
    # Checking for a game 
    if check_nonexsisting_hangman(channel_id):
        raise error.InputError(description="There is currently no hangman game")
    
    for curr_game in HANGMAN:
        if curr_game['channel_id'] == channel_id:
            game = curr_game
            break
    if character in game['char_guess']:
        message.message_send(BOT_TOKEN, channel_id, 'This letter has already been used') 
    word_s = game['word']
    if game['num_guess'] == 15:
        message.message_send(BOT_TOKEN, channel_id, f'No guesses left the word was {word_s}. You Lose :(') 
        hangman_stop(BOT_TOKEN, channel_id)
    
    if character in game['word']:
        game['char_guess'].append(character)
    
    game['num_guess'] += 1
    
    return hangman_state_initialise(game, channel_id)

def hangman_state_initialise(game, channel_id): #pragma: no cover
    """
    initialise the game 
    """
    hangman_state = ''
    for char in game['word']:
        if char in game['char_guess']:
            hangman_state += char
            game['state'] = game['state'].replace(char, '')
        elif char == ' ':
            hangman_state += ' '
        else:
            hangman_state += '_ '
    hangman_state += '\n'
    if check_exsisting_hangman(channel_id):
        message.message_send(BOT_TOKEN, game['channel_id'], hangman_state) 
    
    if game['state'] == '':
        message.message_send(BOT_TOKEN, channel_id, 'Congratulations you guessed the word correctly!') 
        hangman_stop(BOT_TOKEN, channel_id)

def hangman_stop(token, channel_id): #pragma: no cover
    '''
    Stop the game
    '''
    for curr_game in HANGMAN:
        if curr_game['channel_id'] == channel_id:
            HANGMAN.remove(curr_game)
            break
    message.message_send(BOT_TOKEN, channel_id, r"Hangman has ended! *\(^v^)/*") 
 
def hangman_reveal(token, channel_id): #pragma: no cover
    """
    reveal answer and end the game
    """
    #If token valid
    if helper_token_valid(token):
        raise error.AccessError(description="Invalid token")

    #If channel valid
    if helper_channel_valid(channel_id):
        raise error.AccessError(description="Channel_id invalid")
    
    # Checking for a game 
    if check_nonexsisting_hangman(channel_id):
        raise error.InputError(description="There is currently no hangman game")

    for curr_game in HANGMAN:
        if curr_game['channel_id'] == channel_id:
            word_s = curr_game['word']
            message.message_send(BOT_TOKEN, channel_id, f'The word was {word_s}. You Lose :(') 
    
    return hangman_stop(token, channel_id)