from xml.dom import minidom

import requests


def save_app_list(sitemap):
    urls = []
    res = requests.get(sitemap)
    xmldoc = minidom.parseString(res.text)
    itemlist = xmldoc.getElementsByTagName("loc")
    for s in itemlist:
        # if str(s.childNodes[0].nodeValue).split('/')[3].split('-')[2] == 'fa':
        print(s.childNodes[0].nodeValue)
        urls.append(s.childNodes[0].nodeValue)

    apps = []

    for url in urls:
        print(url)
        try:
            res = requests.get(url.strip())
        except requests.exceptions.ConnectionError:
            try:
                while res.status_code != 200:
                    res = requests.get(url)
            except:
                pass
        print(res.status_code)
        xmldoc = minidom.parseString(res.text)
        itemlist = xmldoc.getElementsByTagName("loc")
        for s in itemlist:
            apps.append(s.childNodes[0].nodeValue.split('/')[4].strip())
    with open(f"{sitemap.split('/')[2].split('.')[0]}_apps.txt", "a") as f:
        for app in apps:
            f.write(app)
            f.write('\n')


if __name__ == '__main__':
    save_app_list("https://cafebazaar.ir/app-sitemap.xml")
    save_app_list("https://myket.ir/sitemap.xml")
