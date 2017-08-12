import requests
import json
from requests.adapters import HTTPAdapter
# Hackerrank API endpoint
RUN_API_ENDPOINT = 'http://api.hackerrank.com/checker/submission.json'

# supported languages and their codes passed to API
LANG_CODE = {'fsharp': 33, 'javascript': 20, 'whitespace': 41, 'python': 5, 'lolcode': 38, 'mysql': 10, 'fortran': 54,
             'tcl': 40, 'oracle': 11, 'pascal': 25, 'haskell': 12, 'cobol': 36, 'octave': 46, 'csharp': 9, 'go': 21,
             'php': 7, 'ruby': 8, 'java8': 43, 'bash': 14, 'visualbasic': 37, 'groovy': 31, 'c': 1, 'erlang': 16,
             'java': 3, 'd': 22, 'scala': 15, 'tsql': 42, 'ocaml': 23, 'perl': 6, 'lua': 18, 'xquery': 48, 'r': 24,
             'swift': 51, 'sbcl': 26, 'smalltalk': 39, 'racket': 49, 'cpp': 2, 'db2': 44, 'objectivec': 32,
             'clojure': 13, 'python3': 30, 'rust': 50}


class HackerRankAPI():
    # initialize the API object
    def __init__(self, api_key):
        self.params_dict = {}
        self.params_dict['api_key'] = api_key
        self.params_dict['format'] = 'json'

    # run given piece of code
    def run(self, code):
        self.manage_params(code)
        response = self.__request(RUN_API_ENDPOINT, self.params_dict)
        result = Result(response.json()['result'])  # create a result object of Result class
        return result

    # update params_dict with code data
    def manage_params(self, code):
        self.params_dict['source'] = code['source']
        self.params_dict['lang'] = self.getLangCode(code['lang'])
        if 'testcases' in code:
            self.params_dict['testcases'] = json.dumps(code['testcases'])
        else:
            self.params_dict['testcases'] = json.dumps([""])  # empty testcase

    # send API request
    def __request(self, url, params):
        try:
            s=requests.Session()
            a=HTTPAdapter(max_retries=20)
            s.mount('http://',a)
            response = s.post(url, data=params)
            return response
        except Exception as e:
            print(e)

    # utility function to get language code to be passed as parameter to API
    def getLangCode(self, lang):
        try:
            return LANG_CODE[lang]
        except KeyError:
            print(
                "%s language not recognized.Use function supportedlanguages() to see the list of proper names of allowed languages." % lang)
            return -1

    # get list of all supported languages
    def supportedlanguages(self):
        return LANG_CODE.keys()


# to convert json to a class object of Result
class Result():
    def __init__(self, result):
        self.error = result['stderr']
        self.output = result['stdout']
        self.memory = result['memory']
        self.time = result['time']
        self.message = result['compilemessage']