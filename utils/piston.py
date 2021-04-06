# REX.py - code-running stuff is handled here
# the code above just sends request to Rextester API
# and works a little bit on the response, that's it
import traceback

import requests
import json
import re
import ast
from core.strings import Strings
from core import constants

strings = Strings()


class Rex:
    """
    To store Rextester API response
    """
    def __init__(self, errors=None, result=None, stats=None, success=None):
        self.errors = errors
        self.result = result
        self.stats = stats
        self.success = success


class Interpreter(object):
    """
    The only reason why we are implementing a class is that we are going to implement new feats
    which needs additional function and it is always better to group related functions
    """

    def detect_input(self, code_text: str) -> [bool, int, int]:
        """
        We will check the code and try our best to detect input
        :param code_text: string representation of code
        :return: boolean showing if there is an input call or not, line number where the input found and index
        """
        pattern = "input\s*\("
        quote, double_quote, hashtag = "'", '"', '#'
        # we are going to check each line
        for line_number, line in enumerate(code_text.splitlines()):
            # line might be a comment, if it is, we need to ignore the line where commenting starts
            quote_open = False
            double_quote_open = False
            bools = [True, False]
            clean_line_string = ''
            for index, char in enumerate(line):
                if char == quote:
                    quote_open = bools[quote_open] and not double_quote_open
                elif char == double_quote:
                    double_quote_open = bools[double_quote_open] and not quote_open
                elif char == hashtag:
                    # if quote and double quotes are not open,
                    # this means, we reached the commenting point
                    if not quote_open and not double_quote_open:
                        break
                else:
                    if not quote_open and not double_quote_open:
                        clean_line_string += char
            # now that we have a clean line without strings and comments, we can assume that
            # if we find input() pattern, there is an input function call
            search_result = re.search(pattern, clean_line_string)
            if search_result:
                # we found an input function call
                return True, line_number + 1, search_result.start()
        # either we failed to detect input function call or there is not any
        return False, 0, 0

    def advanced_input_detection(self, code_string: str) -> bool:
        """
        Another version of input detection with built-in ast module.
        Since we are using Abstract Syntax Tree, there is a pretty high chance that
        we will find it if there is any input function call inside code
        :param code_string: code string
        :return: boolean
        """
        try:
            # parse the string to AST object
            parsed_code = ast.parse(code_string)
            # walk through each node and search for input call
            for node in ast.walk(parsed_code):
                if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                    if node.func.id == 'input':
                        # we've just found a input() fucntion call
                        return True
            # probably there is no input() function call (we might've missed it tho)
        except:
            # we might get syntax error while checking, we just skip it
            pass
        return False

    def detect_code(self, text) -> [bool, int]:
        """
        Used to detect if text is a runnable code or not
        :param text: input string to be checked
        :return: boolean indicating whether it is code or not, language code (if it is code)
        """
        # it is enough to check only the first line
        first_line = text.splitlines()[0]
        prefixes = [('#py2', 5), ('#py3', 24), ('#py', 24)]
        for prefix, language_code in prefixes:
            if first_line.startswith(prefix):
                # this is runnable code and we already know the language
                return True, language_code
        return False, -1

    def run(self, lang: int, code: str, input_data: str = "") -> Rex:
        """
        To run code using Rextester API
        :param lang: language string
        :param code: code to run
        :param input_data: optional input data
        :return: instance of Rex class including serialized API response
        """
        try:
            url = "https://emkc.org/api/v1/piston/execute"
            payload = {"language": "py3", "source": code, "stdin": input_data}
            request = requests.post(url, json=payload)
            json_obj = request.json()
            errors = json_obj['stderr']
            result = json_obj['output']
            stats = ""
            success = not errors
            rex = Rex(errors, result, stats, success)
            return rex
        except:
            print(traceback.format_exc())
            errors = strings.code_server_fatal_error
            result = ""
            stats = ""
            return Rex(result=result, errors=errors, stats=stats)

    def format_response(self, response) -> str:
        """
        Turn Rex instance into decorated string
        :param response: Rex instance
        :return: output string
        """
        if response.errors:
            # there was error(s)
            return strings.code_result_error_template.format(errors=strings.clean_html(response.errors))
        elif len(response.result) > constants.DEFAULT_CODE_RESPONSE_LENGTH_LIMIT:
            return strings.code_response_too_long.format(limit=constants.DEFAULT_CODE_RESPONSE_LENGTH_LIMIT)
        return strings.code_result_template.format(result=strings.clean_html(response.result))
