import requests
import urllib, urllib2, json
import cookielib
import ssl
def login_nbu():

    url_head = 'https://93.1.115.142/opscenter/loadLogin.do'


    user_agent = r'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko'
    head = {'User-Agent': user_agent, 'Content-Type': 'application/json;charset=UTF-8', 'Cache-Control': 'max-age=0', 'If-Modified-Since': bytes(0), 'Accept': '*/*', 'X-Requested-With': 'XMLHttpRequest'}
    payload = "userName=admin&password=Password123"
    req = requests.post(url=url_head, headers=head,verify=False,data=payload)
    print req.status_code


if __name__ == '__main__':
    login_nbu()


