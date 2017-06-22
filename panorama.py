import re, xlwt, json, os
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString  # pip install beautifulsoup4
import requests

wish_list = ['produkcja', 'masarnia', 'rzeźnia', 'przepompownia', 'oczyszczalnia', 'basen', 'tartak', 'silos',
             'suszarnia', 'mięsne', 'silos', 'silosy', 'lodowisko', 'produkcja']

class Panorama:

    def __init__(self):
        #base_href = 'http://panoramafirm.pl/szukaj/dolno%C5%9Bl%C4%85skie,k%C5%82odzki,k%C5%82odzko/firmy,#.html' # 'http://panoramafirm.pl/szukaj/dolno%C5%9Bl%C4%85skie,ole%C5%9Bnicki,ole%C5%9Bnica/firmy,#.html'
        #base_href = 'http://panoramafirm.pl/tartak/dolno%C5%9Bl%C4%85skie/firmy,#.html'
        base_href = 'http://panoramafirm.pl/'+what+'/firmy,#.html'
        href_list = []

        base_url = base_href.replace('#', '1')
        html = requests.get(base_url).content

        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            if 'title' in link.attrs:
                cl = link.get('title')
                if 'do ostatniej strony' in cl:
                    last_page = link.get('href')

        last_page_rev = last_page[::-1]
        last_page_comma = last_page_rev.split(',')[0]
        page_count = int(last_page_comma[::-1][:-5])


        for i in range(page_count):
            href_list.append(base_href.replace('#', str(i)))

        open('json_'+what+'.txt', 'w').close()
        ssmax = '~'+str(len(href_list)*25)
        now = -1

        for href in href_list:
            html = requests.get(href).content
            soup = BeautifulSoup(html, 'html.parser')

            company_links = soup.find_all('a')
            smax = str(len(company_links))

            for next_link in company_links:
                if 'title' in next_link.attrs:
                    if 'Zobacz informacje' in next_link.get('title'):
                        now += 1
                        print(what+':'+str(now)+'/'+ssmax+'->'+next_link.get('href'))  # dubstep dziwko
                        #print(str(Panorama.company_content(next_link.get('href'))))

                        with open('json_'+what+'.txt', 'a+') as f:
                            try:
                                cc = Panorama.company_content(next_link.get('href'))
                                cc['link'] = href
                                f.write(json.dumps(cc)+'\n')
                                f.close()
                            except:
                                exc = open('exception.txt', 'a+')
                                exc.write(what+': '+str(next_link))
                                exc.close()
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
        result['wojewodztwo'] = second_split[0]
        result['powiat'] = second_split[1]
        result['miejscowosc'] = second_split[2]
        result['ulica'] = str(second_split[3:]).replace('[','').replace(']','').replace('\'','').replace(',',' ').replace('_', ' ')

        return result

    @staticmethod
    def json_to_xls():
        with open('json_'+what+'.txt', 'r') as f:
            lines = f.readlines()
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('PanoramaFirm')
        col_order = ['wojewodztwo', 'powiat', 'miejscowosc', 'ulica', 'nazwa', 'telefon']
        row = 0
        for line in lines:
            try:
                row += 1
                json_dict = json.loads(line)
                for col in col_order:
                    try:
                        sheet.write(row, col_order.index(col), json_dict[col])
                    except:
                        continue
            except:
                pass
        workbook.save('ekscel-'+what+'.xls')

for what_now in wish_list:
    what = what_now
    p = Panorama()
    p.json_to_xls()
    exit()

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
