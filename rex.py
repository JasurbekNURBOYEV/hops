# REX.py - code-running stuff is handled here
# the code above just sends request to Rextester API
# and works a little bit on the response, that's it

import requests
import json


def run(lang, code):
    
    languages = {
     'python': 24,
     'python2': 5,
     'python3': 24,
     'php': 8
    }
    
    try:
     if type(lang) == str:
      lang = languages[lang]
    except:
     raise ValueError("Couldn't find the language: {}".format(lang))
     
    class Rex:
        errors = result = stats = str
        success = bool

        def __init__(self, errors=None, result=None, stats=None, success=None):
            self.errors = errors
            self.result = result
            self.stats = stats
            self.success = success

    url = "https://rextester.com/rundotnet/api"
    payload = {"LanguageChoice": lang, "Program": code}
    request = requests.post(url, data=payload)
    result = request.text
    json_obj = json.loads(result)
    errors = json_obj['Errors']
    result = json_obj['Result']
    stats = json_obj['Stats']
    success = True if not errors else False
    rex = Rex(errors, result, stats, success)
    return rex
