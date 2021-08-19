# --- START: IMPORTS

# bult-in
# local
# django-specific
from django.conf import settings

# other/external
# --- END: IMPORTS


# commands
COMMAND_START = 'start'
COMMAND_TEST = 'test'
COMMAND_CANCEL = 'cancel'
COMMAND_TAGS = 'tags'

# command data prefixes
CMD_DATA_START_TEST = 'test'
CMD_DATA_BOOK_COMMENT = 'bookcomment'
CMD_DATA_RULES = 'rules'

# user statuses
USER_STATUS_LEFT = 'left'
USER_STATUS_ADMIN = 'administrator'
USER_STATUS_OWNER = 'creator'

# steps
STEP_INITIAL_POINT = 0

# TEST steps [100-199]
STEP_TEST_WAITING_TO_START = 100
STEP_TEST_ONGOING = 101
STEP_TEST_WAITING_FOR_CERTIFICATE = 102

# AGREEMENT steps [200-299]
STEP_AGREEMENT_WAITING_TO_START = 200
STEP_AGREEMENT_WAITING_FOR_CONFIRMATION = 201

# test configs
TEST_MIN_PASSING_SCORE_PERCENTAGE = 0.6
TEST_CLASSES_BY_RESULT = [
    ("A", 1.0, 7),  # name, passing score percentage (scaled to 1) and daily limit
    ("B", 0.9, 6),
    ("C", 0.8, 5),
    ("D", 0.7, 4),
    ("E", 0.6, 3),
]

# callback data
CALLBACK_DATA_HEADER_SEPARATOR = '_'
CALLBACK_DATA_SEPARATOR = '|'
CALLBACK_DATA_HEADER_TEST = 'test'
CALLBACK_DATA_HEADER_START_TEST = 'starttest'
CALLBACK_DATA_START_TEST_TEMPLATE = CALLBACK_DATA_HEADER_SEPARATOR.join(
    [
        CALLBACK_DATA_HEADER_START_TEST,
        CALLBACK_DATA_SEPARATOR.join(
            [
                "{uid}"
            ]
        )
    ]
)
CALLBACK_DATA_HEADER_NEW_MEMBER = 'newmember'
CALLBACK_DATA_TEST_TEMPLATE = CALLBACK_DATA_HEADER_SEPARATOR.join(
    [
        CALLBACK_DATA_HEADER_TEST,
        CALLBACK_DATA_SEPARATOR.join(
            ["{uid}", "{quiz_id}", "{index}", "{option_id}", "{current_score}"]
        )
    ]
)
CALLBACK_DATA_NEW_MEMBER_TEMPLATE = CALLBACK_DATA_HEADER_SEPARATOR.join(
    [
        CALLBACK_DATA_HEADER_NEW_MEMBER,
        CALLBACK_DATA_SEPARATOR.join(
            ["{uid}", "{chat_id}"]
        )
    ]
)

# default configs
DEFAULT_PARSE_MODE = "html"
DEFAULT_INPUT_HEADER = 'inp\n'
DEFAULT_CERT_LIMIT = 3
DEFAULT_TEMP_MEDIA_FOLDER = 'temp'
DEFUALT_RESTRICTION_SECONDS = 3600
DEFAULT_BAN_LIMIT_SECONDS = 720 * 3600  # it is 720 hours in total, any user exceeding this limit will be banned
DEFAULT_CODE_RESPONSE_LENGTH_LIMIT = 3000

# allowed groups
ALLOWED_CHATS = [settings.MAIN_GROUP_ID, settings.TEST_GROUP_ID, settings.BOARD_GROUP_ID]

# admins
ADMIN_ALERT_KEYWORD = '@admins'
ADMIN_CMD_HEADER = 'sudo '
ADMIN_CMD_RO = 'ro'
ADMIN_CMD_UNRO = 'unro'
ADMIN_CMD_CHECK = 'check'

# Greed Island commands
ADMIN_CMD_MARK_AS_QUESTION = 'maq'
ADMIN_CMD_MARK_AS_ANSWER = 'maa'
ADMIN_CMD_REMOVE_QUESTION_TAG = 'rmt'


# tips
TIPS_HEADER = '!'

# tags
TAG_PREFIX = '#'
