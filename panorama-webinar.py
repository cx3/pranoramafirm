import re, xlwt, json, os
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString  # pip install beautifulsoup4
import requests


def panorama_firm(what, where):

    if not isinstance(what, str):
        return 'Error: what is not str'
    if not isinstance(where, str):
        return 'Error: where is not str'

    what = what.encode('1252', 'ignore').decode('1252')
    where = where.encode('1252', 'ignore').decode('1252')

    print(what)
    print(where)

    panorama_query = 'http://' + 'panoramafirm.pl/szukaj?k='+'@'+'&l='+'#'

    panorama_query = panorama_query.replace('@', what).replace('#', where)

    print('query='+str(panorama_query))

    base_href = 'http://panoramafirm.pl/szukaj/dolno%C5%9Bl%C4%85skie,k%C5%82odzki,k%C5%82odzko/firmy,#.html'  # 'http://panoramafirm.pl/szukaj/dolno%C5%9Bl%C4%85skie,ole%C5%9Bnicki,ole%C5%9Bnica/firmy,#.html'
    href_list = []

    for i in range(len(base_href)):
        href_list.append(base_href.replace('#', str(i)))

    thread_count = 4
    part_len = int(len(href_list)/thread_count)

    href_list_split = []

    href_list_split.append(href_list[0:part_len])

    stop = -1
    for i in range(1, thread_count):
        start = i*part_len
        stop = (i+1)*part_len
        if not i == thread_count - 1:
            href_list_split.append(href_list[start:stop])
        else:
            href_list_split.append(href_list[start:len(href_list)])

    print('stop='+str(stop))


    for hl in href_list_split:
        for h in hl:
            print(h)
        print('-'*44)

panorama_firm('tartak', 'dolnośląskie')





def _sub_process(href_list):
    for href in href_list:
        html = requests.get(href).content
        soup = BeautifulSoup(html, 'html.parser')

        company_links = soup.find_all('a')

        for next_link in company_links:
            if 'title' in next_link.attrs:
                if 'Zobacz informacje' in next_link.get('title'):
                    print(next_link.get('href'))  # cool stuff
                    # print(str(Panorama.company_content(next_link.get('href'))))

                    with open('json.txt', 'a+') as f:
                        cc = company_content(next_link.get('href'))
                        cc['link'] = href
                        f.write(json.dumps(cc) + '\n')
                        f.close()
        print('-' * 44)


def company_content(company_href):
    html = requests.get(company_href).content
    soup = BeautifulSoup(html, 'html.parser')
    h1s = soup.find_all('h1')

    result = {}

    for h1 in h1s:
        if 'class' in h1.attrs:
            s = str(h1)
            pos = s.index('\">') + 2
            result['nazwa'] = s[pos:].replace('</h1>', '')
    ps = soup.find_all('p')
    for p in ps:
        if 'class' in p.attrs:
            if 'marginTop10' in p.get('class'):
                s = str(p)
                pos = s.index('\">') + 2
                result['adres'] = s[pos:].replace('<br/>', ' ').replace('<br>', ' ').replace('</p>', ' ')
    a_ = soup.find_all('a')
    for a in a_:
        if 'data-for-copy' in a.attrs:
            result['telefon'] = a.get('data-for-copy')
    first_split = company_href.split('/')[3]
    second_split = first_split.split(',')
    result['wojewodztwo'] = second_split[0]
    result['powiat'] = second_split[1]
    result['miejscowosc'] = second_split[2]
    result['ulica'] = str(second_split[3:]).replace('[', '').replace(']', '').replace('\'', '').replace(',',
                                                                                                        ' ').replace(
        '_', ' ')

    return result



def json_to_xls():
    with open('json.txt', 'r') as f:
        lines = f.readlines()
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('PanoramaFirm')
    col_order = ['wojewodztwo', 'powiat', 'miejscowosc', 'ulica', 'nazwa', 'telefon']
    row = 0
    for line in lines:
        row += 1
        json_dict = json.loads(line)
        for col in col_order:
            try:
                sheet.write(row, col_order.index(col), json_dict[col])
            except:
                continue
    workbook.save('ekscel.xls')




'''
class PanoramaWroclaw:

    def __init__(self):
        base_href = 'http://panoramafirm.pl/wroc%C5%82aw/firmy,#.html'
        href_list = []

        for i in range(0, 75, 1):
            href_list.append(base_href.replace('#', str(i)))

        open('json-wroc.txt', 'w').close()

        now_site = -1
        stop_at = str(len(href_list))
        for href in href_list:
            now_site += 1
            print(str(now_site)+'/'+stop_at)
            html = requests.get(href).content
            soup = BeautifulSoup(html, 'html.parser')
            try:
                company_links = soup.find_all('a')
                for next_link in company_links:
                    if 'title' in next_link.attrs:
                        if 'Zobacz informacje' in next_link.get('title'):
                            print(next_link.get('href'))  # cool stuff
                            # print(str(Panorama.company_content(next_link.get('href'))))
                            with open('json-wroc.txt', 'a+') as f:
                                cc = Panorama.company_content(next_link.get('href'))
                                cc['link'] = href
                                f.write(json.dumps(cc) + '\n')
                                f.close()
            except:
                print('EXCEPTION at href='+href)
            print('-'*44)

    @staticmethod
    def company_content(company_href):
        html = requests.get(company_href).content
        soup = BeautifulSoup(html, 'html.parser')
        h1s = soup.find_all('h1')

        result = {}

        for h1 in h1s:
            if 'class' in h1.attrs:
                s = str(h1)
                pos = s.index('\">')+2
                result['nazwa'] = s[pos:].replace('</h1>', '')
        ps = soup.find_all('p')
        for p in ps:
            if 'class' in p.attrs:
                if 'marginTop10' in p.get('class'):
                    s = str(p)
                    pos = s.index('\">') + 2
                    result['adres'] = s[pos:].replace('<br/>', ' ').replace('<br>', ' ').replace('</p>', ' ')
        a_ = soup.find_all('a')
        for a in a_:
            if 'data-for-copy' in a.attrs:
                result['telefon'] = a.get('data-for-copy')
        first_split = company_href.split('/')[3]
        second_split = first_split.split(',')
        result['wojewodztwo'] = 'dolnośląskie'
        result['powiat'] = 'wrocławski'
        result['miejscowosc'] = 'wrocław'
        result['ulica'] = str(second_split[3:]).replace('[','').replace(']','').replace('\'','').replace(',',' ').replace('_', ' ')

        return result

    @staticmethod
    def json_to_xls():
        with open('json-wroc.txt', 'r') as f:
            lines = f.readlines()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('PanoramaFirm')
        col_order = ['wojewodztwo', 'powiat', 'miejscowosc', 'ulica', 'nazwa', 'telefon']
        row = 0
        for line in lines:
            row += 1
            json_dict = json.loads(line)
            for col in col_order:
                try:
                    sheet.write(row, col_order.index(col), json_dict[col])
                except:
                    continue
        workbook.save('ekscel-wroc.xls')'''
