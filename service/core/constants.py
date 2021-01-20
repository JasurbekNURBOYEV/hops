# commands
COMMAND_START = 'start'
COMMAND_TEST = 'test'
COMMAND_CANCEL = 'cancel'


# command data prefixes
CMD_DATA_START_TEST = 'start_test'
CMD_DATA_BOOK_COMMENT = 'bookcomment'

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
CALLBACK_DATA_SEPARATOR = '-'
CALLBACK_DATA_HEADER_TEST = 'test'
CALLBACK_DATA_TEST_TEMPLATE = CALLBACK_DATA_HEADER_SEPARATOR.join(
    [
        CALLBACK_DATA_HEADER_TEST,
        CALLBACK_DATA_SEPARATOR.join(
         ["{uid}", "{quiz_id}", "{index}", "{option_id}", "{current_score}"]
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
