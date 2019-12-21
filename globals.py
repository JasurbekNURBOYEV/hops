# GLOBALS.py - no joke, it is just a bunch of global variables

import telebot
dev = 191407555  # replace this with your ID, it is my ID (@FutureDreams)
bot_id = 346754312  # replace this with your bot's ID, this is actually @Hopsrobot's ID
python_uz = -1001050555471  # this is the ID of our Python UZBEKISTAN group: @python_uz
test_group = -1001172204177  # this is the ID of private tet group, change it to yours
allowed_groups = [python_uz, test_group, -154767078, -1001092437278]  # modify this to allow groups
verified = [dev]  # modify this to add verified accounts, verified accounts won't get banned or restricted
should_log = True  # set it to False, and log function doesn't work
botlink = 'YOUR_BOTS_USERNAME'  # if your bot is @wonerbot, just write 'wonderbot'
token = "YOUR_BOT_TOKEN"  # this is your bot's token which you can get from @Botfather
telegraph_token = 'YOUR_TOKEN_OF_TELEGRAPH_ACCOUNT'  # your Telegraph accounts' token, Google it to get more info
bot = telebot.TeleBot(token)  # single instance of bot
