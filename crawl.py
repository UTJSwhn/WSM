from bs4 import BeautifulSoup
from urllib.parse import quote
import urllib.request
import urllib.error
import string
import random
import time
import csv
import re
import os

# text_url = 'http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/4/8/9/6/48966/48966-0.txt'
# text_url = 'http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/4/8/9/6/48966/48966-h/48966-h.htm'
# text_url = 'https://www.gutenberg.org/ebooks/search/?query=Kafka'
# text_url = 'http://www.gutenberg.org/ebooks/6619'
# data = urllib.request.urlopen(text_url).read()
# data = data.decode('UTF-8')
# with open('test.html', 'w', encoding='utf-8') as f:
#     f.write(data)

# zip_url = 'http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/6/6/1/6619/6619.zip'
# urllib.request.urlretrieve(zip_url, 'test.zip')


# To obtain the Nobel literature prize winners' work, we need to know who they are first.
class Investigator:
    def __init__(self, target_url='https://en.wikipedia.org/wiki/List_of_Nobel_laureates_in_Literature'):
        self.target_url = target_url
        self.headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        }
        self.authors_page = None

    def fetch(self):
        req = urllib.request.Request(url=self.target_url, headers=self.headers, method='GET')
        self.authors_page = urllib.request.urlopen(req).read().decode('UTF-8')

    def parse(self):
        html = BeautifulSoup(str(self.authors_page), 'lxml')
        author_table = html.find(name='tbody').find_all(name='tr')

        result = []

        for author_information in author_table:
            info_list = author_information.find_all(name='td')
            if len(info_list) == 7:
                year = info_list[0].string[:4]
                image_dom = info_list[1]
                if image_dom.find(name='img'):
                    image = image_dom.find(name='img')['src'][2:]
                else:
                    image = ''
                author = info_list[2].find(name='a').string
                country = info_list[3].find(name='a').string
                language = info_list[4].find(name='a').string
                re_pattern = re.compile(r'\"(.*)\"')
                re_result = re_pattern.findall(info_list[5].text)
                if len(re_result) == 0:
                    re_pattern = re.compile('“(.*)”')
                    re_result = re_pattern.findall(info_list[5].text)
                citation = re_result[0]

                result.append({
                    'time': year,
                    'image': image,
                    'author': author,
                    'country': country,
                    'language': language,
                    'citation': citation
                })
            elif len(info_list) == 6:
                year = result[-1]['time']
                image_dom = info_list[0]
                if image_dom.find(name='img'):
                    image = image_dom.find(name='img')['src'][2:]
                else:
                    image = ''
                author = info_list[1].find(name='a').string
                country = info_list[2].find(name='a').string
                language = info_list[3].find(name='a').string
                re_pattern = re.compile(r'\"(.*)\"')
                re_result = re_pattern.findall(info_list[4].text)
                if len(re_result) == 0:
                    re_pattern = re.compile('“(.*)”')
                    re_result = re_pattern.findall(info_list[4].text)
                citation = re_result[0]

                result.append({
                    'time': year,
                    'image': image,
                    'author': author,
                    'country': country,
                    'language': language,
                    'citation': citation
                })

        return result


def auto_download(url, file_name):
    try:
        urllib.request.urlretrieve(url, file_name)
    except urllib.error.ContentTooShortError:
        print('Network conditions are not good. Reloading')
        auto_download(url, file_name)


if __name__ == '__main__':
    Q = Investigator()
    Q.fetch()
    author_list = Q.parse()

    if not os.path.exists('authors.csv'):
        author_file = open('authors.csv', 'w', encoding='utf-8', newline='')
        writer = csv.DictWriter(author_file, fieldnames=['time', 'image', 'author', 'country', 'language', 'citation'])
        writer.writeheader()
        for author_info in author_list:
            writer.writerow(author_info)
        author_file.close()

    for author_info in author_list:
        if author_info['time'] < '1946':
            continue

        author_path = 'books/' + ''.join(author_info['author'].split(' '))
        if not os.path.exists(author_path):
            os.mkdir(author_path)

        if not os.path.exists(author_path + '/' + 'bookList.html'):
            author_query = '+'.join(author_info['author'].split(' '))
            author_url = quote('https://www.gutenberg.org/ebooks/search/?query=' + author_query, safe=string.printable)

            headers = {
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            }
            author_page = urllib.request.urlopen(urllib.request.Request(author_url, headers=headers)).read().decode('utf-8')
            with open(author_path + '/' + 'bookList.html', 'w', encoding='utf-8') as f:
                f.write(author_page)

            random_interval = random.uniform(1, 3)
            time.sleep(random_interval)
        else:
            html_file = open(author_path + '/' + 'bookList.html', 'r', encoding='utf-8')
            author_page = html_file.read()

        author_html = BeautifulSoup(str(author_page), 'lxml')
        item_list = author_html.find(name='ul').findAll(name='li')
        author_info['books'] = []

        start_time = time.time()
        for item in item_list:
            if 'booklink' not in item.attrs['class']:
                continue
            image_span = item.findAll(name='span')[0]
            if 'with-cover' not in image_span.attrs['class']:
                continue
            else:
                book_image_url = image_span.find('img').attrs['src']

            info_span_list = item.findAll(name='span')[1].findAll(name='span')
            if len(info_span_list) == 3:
                if info_span_list[0].string.endswith(')'):
                    continue
                author_match = True
                for character in author_info['author']:
                    if character.isupper() and (character not in info_span_list[1].string):
                        author_match = False
                        break

                name_piece_1 = info_span_list[1].string.split(' ')
                name_piece_2 = author_info['author'].split(' ')
                if name_piece_2[-1] not in name_piece_1:
                    author_match = False

                if author_match:
                    book_id = item.find(name='a').attrs['href'][8:]
                    author_info['books'].append(book_id)
                    book_url = 'http://www.mirrorservice.org/sites/ftp.ibiblio.org/pub/docs/books/gutenberg/'
                    for num in book_id[:-1]:
                        book_url += num + '/'
                    book_url += book_id + '/'

                    file_page = urllib.request.urlopen(book_url).read().decode('UTF-8')
                    file_html = BeautifulSoup(str(file_page), 'lxml')
                    file_dom = file_html.find(name='pre').findAll(name='a')
                    file_list = []
                    for dom in file_dom:
                        file_list.append(dom.string)

                    if book_id + '-h.zip' in file_list:
                        book_url += book_id + '-h.zip'
                    elif book_id + '.zip' in file_list:
                        book_url += book_id + '.zip'
                    elif book_id + '-0.zip' in file_list:
                        book_url += book_id + '-0.zip'
                    elif book_id + '-8.zip' in file_list:
                        book_url += book_id + '-8.zip'
                    else:
                        print('Error: Invalid File Type')
                        continue

                    auto_download(book_url, author_path + '/' + book_id + '.zip')
                    print('Book ' + book_id + ' download finished.')

        end_time = time.time()
        print('The ' + str(len(author_info['books'])) + ' book(s) of ' + author_info['author'] + ' have been downloaded, '
              + str(end_time - start_time) + 's elapsed.')
