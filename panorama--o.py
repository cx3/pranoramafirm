import re, xlwt, json, os, sys, optparse, requests
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString  # pip install beautifulsoup4

class Panorama:

    def __init__(self):
        #base_href = 'http://panoramafirm.pl/szukaj/dolno%C5%9Bl%C4%85skie,ole%C5%9Bnicki,ole%C5%9Bnica/firmy,#.html'
        base_href = 'http://panoramafirm.pl/szukaj?k=&l=k%C5%82odzko'
        href_list = []

        for i in range(110):
            href_list.append(base_href.replace('#', str(i)))

        open('json.txt', 'w').close()

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
                            cc = Panorama.company_content(next_link.get('href'))
                            cc['link'] = href
                            f.write(json.dumps(cc)+'\n')
                            f.close()
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
        result['ulica'] = str(second_split[3:]).replace('[', '').replace(']', '').replace('\'', '')\
            .replace(',', ' ').replace('_', ' ')

        return result

    @staticmethod
    def json_to_xls(filename='json.txt'):
        with open(filename, 'r') as f:
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
                except KeyError:
                    continue
        workbook.save('ekscel.xls')

# --------------------------------------------------------------------------------------
'''
arg_len = len(sys.argv)

if arg_len > 1:
    if sys.argv[1] == "json":
        if arg_len == 3:
            Panorama.json_to_xls(sys.argv[2])
        if arg_len == 2:
            Panorama.json_to_xls()
else:
    Panorama()

# Panorama.json_to_xls()
'''
Panorama()
Panorama.json_to_xls()
