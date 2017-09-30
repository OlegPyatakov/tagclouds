from urllib import request
from bs4 import BeautifulSoup


def gettextfromurl(url):
    if not any(prefix in url for prefix in ('http://', 'https://')):
        url = ''.join(['http://',url])
    try:
        r = request.Request(url)
        r.add_header('User-agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5')

        html = request.urlopen(r).read()
    except:
        return None

    if len(html) > 4 * 1024 * 1024:
        return None

    soup = BeautifulSoup(html,"html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()
    return text
