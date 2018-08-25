import bs4 as bs
import requests
from urllib import parse
from configparser import ConfigParser


class Rating:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.he_login = self.config.get('hackerearth', 'username')
        self.he_password = self.config.get('hackerearth', 'password')
        self.headers = {'User-agent': 'Mozilla/5.0'}

    def hackerearth(self, handle):
        try:
            url = "https://www.hackerearth.com/AJAX/login/"
            session = requests.Session()
            payload = {"login": self.he_login, "password": self.he_password, "submit": "True"}
            headers = {
                'accept': "*/*",
                'origin': "https://www.hackerearth.com",
                'x-requested-with': "XMLHttpRequest",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36 Vivaldi/1.96.1147.55",
                'content-type': "application/x-www-form-urlencoded; boundary=----WebKitFormBoundary",
                'referer': "https://www.hackerearth.com/@gotham13121997",
                'accept-encoding': "gzip, deflate, br",
                'accept-language': "en-US,en;q=0.9",
                'cache-control': "no-cache",
            }
            session.post(url, data=payload, headers=headers)
            response = session.get('https://www.hackerearth.com/@' + handle, headers=self.headers)
            soup = bs.BeautifulSoup(response.text, 'html5lib')
            e404 = soup.find("meta", {"content": "404 error "})
            if e404 is not None:
                return None
            stri = "HACKEREARTH\n"
            for i in soup.find_all('a', {"href": "/users/" + handle + "/activity/hackerearth/#user-rating-graph"}):
                stri = stri + i.text + "\n"
            for i in soup.find_all('a', {"href": "/@" + handle + "/followers/"}):
                stri = stri + i.text + "\n"
            for i in soup.find_all('a', {"href": "/@" + handle + "/following/"}):
                stri = stri + i.text + "\n"
            return stri
        except Exception as e:
            print(e)
            return None
    
    def hackerrank(self, handle):
        try:
            response = requests.get('https://www.hackerrank.com/' + handle + '?hr_r=1', headers=self.headers)
            soup = bs.BeautifulSoup(response.text, 'html5lib')
            try:
                soup.find('script', {"id": "initialData"}).text
            except AttributeError:
                return None
            # I HAVE NO IDEA WHAT I HAVE DONE HERE
            # BUT IT SEEMS TO WORK
            s = soup.find('script', {"id": "initialData"}).text
            i = s.find("hacker_id", s.find("hacker_id", s.find("hacker_id") + 1) + 1)
            i = parse.unquote(s[i:i + 280]).replace(",", ">").replace(":", " ").replace("{", "").replace("}",
                                                                                                         "").replace(
                '"', "").split(">")
            s1 = "HACKERRANK\n"
            for j in range(1, 10):
                s1 = s1 + i[j] + "\n"
            return s1
        except Exception as e:
            print(e)
            return None
    
    def codechef(self, handle):
        try:
            response = requests.get('https://www.codechef.com/users/' + handle, headers=self.headers)
            soup = bs.BeautifulSoup(response.text, 'html5lib')
            try:
                soup.find('a', {"href": "http://www.codechef.com/ratings/all"}).text
            except AttributeError:
                return None
            try:
                s1 = soup.find('span', {"class": "rating"}).text + "\n"
            except AttributeError:
                s1 = ""
            s = "CODECHEF" + "\n" + s1 + "rating: " + soup.find('a', {
                "href": "http://www.codechef.com/ratings/all"}).text + "\n" + soup.find('div', {
                "class": "rating-ranks"}).text.replace(" ", "").replace("\n\n", "").strip('\n')
            return s
        except Exception as e:
            print(e)
            return None
        
    def spoj(self, handle):
        try:
            response = requests.get('http://www.spoj.com/users/' + handle + '/', headers=self.headers)
            soup = bs.BeautifulSoup(response.text, 'html5lib')
            try:
                soup.find('div', {"class": "col-md-3"}).text
            except AttributeError:
                return None
            s = soup.find('div', {"class": "col-md-3"}).text.strip('\n\n').replace("\t", "").split('\n')
            s = s[3].strip().split(":")
            s = "SPOJ\n" + s[0] + "\n" + s[1].strip(" ") + "\n" + soup.find('dl', {
                "class": "dl-horizontal profile-info-data profile-info-data-stats"}).text.replace("\t", "").replace(
                "\xa0", "").strip('\n')
            return s
        except Exception as e:
            print(e)
            return None

    def codeforces(self, handle):
        try:
            response = requests.get('http://codeforces.com/profile/' + handle, headers=self.headers)
            soup = bs.BeautifulSoup(response.text, 'html5lib')
            try:
                soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).text
            except AttributeError:
                return None
            s = soup.find_all('span', {"style": "font-weight:bold;"})
            if len(s) == 0:
                s2 = ""
            else:
                s2 = "contest rating: " + s[0].text + "\n" + "max: " + s[1].text + s[2].text + "\n"
            s1 = "CODEFORCES\n" + s2 + "contributions: " + soup.find('img', {"alt": "User\'\'s contribution into Codeforces community"}).nextSibling.nextSibling.text
            return s1
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def rating_hackerearth(all_data):
        try:
            rat = all_data.split('\n')
            if rat[1] == "Rating":
                rat2 = rat[2].strip(" ").strip("\n")
                return rat2
            return None
        except Exception:
            return None

    @staticmethod
    def rating_hackerrank(all_data):
        try:
            rat = all_data.split('\n')
            rat2 = rat[1].split(" ")[1].strip(" ").strip("\n")
            return rat2
        except Exception:
            return None

    @staticmethod
    def rating_codeforces(all_data):
        try:
            rat = all_data.split("\n")
            if "contest rating:" in rat[1]:
                rat2 = rat[1].split(" ")[2].strip(" ").strip("\n")
                return rat2
            return None
        except Exception:
            return None

    @staticmethod
    def rating_codechef(all_data):
        try:
            rat = all_data.split("\n")
            if not "rating" in rat[1]:
                rat2 = rat[2].split(" ")[1].strip(" ").strip("\n")
                return rat2
            return None
        except Exception:
            return None

    def parse_rating(self, code, all_data):
        if code == 'HE':
            return self.rating_hackerearth(all_data)
        elif code == 'HR':
            return self.rating_hackerrank(all_data)
        elif code == 'CF':
            return self.rating_codeforces(all_data)
        elif code == 'CC':
            return self.rating_codechef(all_data)
        elif code == 'SP':
            return None

    def getAllData(self, code, handle):
        if code == 'HE':
            return self.hackerearth(handle)
        if code == 'HR':
            return self.hackerrank(handle)
        if code == 'CC':
            return self.codechef(handle)
        if code == 'SP':
            return self.spoj(handle)
        if code == 'CF':
            return self.codeforces(handle)
        return None
