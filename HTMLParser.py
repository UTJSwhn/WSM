from bs4 import BeautifulSoup
import json


# import re


class HParser:
    def __init__(self, book_path):
        self.book_path = book_path
        self.book_id = self.book_path.split('/')[-1][:-6]

        self.unescape()
        self.book_path += 'l'
        self.soup = BeautifulSoup(open(self.book_path, encoding='iso-8859-1'), 'lxml')

        self.title, self.author = self.fetch_info()

        self.content = []
        self.parse()

        self.store_json()

    def unescape(self):
        with open(self.book_path, encoding='iso-8859-1') as source_file:
            page = source_file.read()
            page = page.replace('&mdash;', ' -- ')
            page = page.replace('&lsquo;', '\'')
            page = page.replace('&rsquo;', '\'')
            page = page.replace('&ldquo;', '"')
            page = page.replace('&rdquo;', '"')
            page = page.replace('&amp;', '&')
            with open(self.book_path + 'l', 'w+', encoding='iso-8859-1') as target_file:
                print(page, file=target_file)

    @staticmethod
    def trim_sentence(s):
        if s == '':
            return s

        start_index = 0
        while s[start_index] == ' ' or s[start_index] == '\n':
            start_index += 1
            if start_index == len(s):
                break

        end_index = len(s) - 1
        while s[end_index] == ' ' or s[end_index] == '\n':
            end_index -= 1
            if end_index == -1:
                break

        return s[start_index: end_index + 1]

    @staticmethod
    def is_roman_digit(s):
        if s == '':
            return False
        for c in s:
            if c not in ['I', 'V', 'X']:
                return False
        return True

    @staticmethod
    def get_own_text(dom):
        return ''.join(dom.findAll(text=True, recursive=False))

    def fetch_info(self):
        title = self.trim_sentence(self.soup.findAll(name='title')[0].text.split(',')[0])
        author = self.trim_sentence(self.soup.findAll(name='title')[0].text.split('by ')[1])
        return title, author

    def parse(self):
        # Addition Rule: delete foot note (Book id: 690)
        for dom in self.soup.findAll(name='p', attrs={'class': ['foot']}):
            dom.decompose()

        self.soup.findAll(name='pre')[-1].decompose()

        chapters = []
        hrefs = []

        # some special case
        # chapter_container = 'td'
        # chapter_container = 'p'
        for dom in self.soup.findAll(['p', 'h3']):
            chapter_dom = dom.findAll(name='a')
            if len(chapter_dom) == 0:
                continue

            if len(self.trim_sentence(self.get_own_text(dom))) != 0:
                continue

            if 'href' in chapter_dom[0].attrs:
                chapters.append(chapter_dom[0].text)
                hrefs.append(chapter_dom[0].attrs['href'][1:])

        print(chapters)

        chapter_index = -1
        paragraph_block = []

        # Tags for special case (e.g. book 1321)
        text_doms = self.soup.findAll(['a', 'p', 'h2', 'h3', 'pre'])

        # Standard Tags
        # text_doms = self.soup.findAll(['a', 'p', 'h2', 'h3'])
        for i in range(len(text_doms)):
            dom = text_doms[i]
            if i == len(text_doms) - 1 or ('name' in dom.attrs and chapter_index != len(chapters) - 1 and dom.attrs['name'] == hrefs[chapter_index + 1]):
                if i == len(text_doms) - 1:
                    s = self.trim_sentence(dom.text)
                    if len(s):
                        paragraph_block.append(s)
                if chapter_index >= 0:
                    self.content.append({
                        "name": chapters[chapter_index],
                        "sub_name": "",
                        "text": paragraph_block
                    })
                paragraph_block = []
                chapter_index += 1
            else:
                s = self.trim_sentence(dom.text)
                if len(s):
                    paragraph_block.append(s)

        for chapter in self.content:
            print(chapter)

    def store_json(self):
        json_object = {
            "id": self.book_id,
            "title": self.title,
            "author": self.author,
            "content": self.content
        }

        with open('data_1/' + self.book_id + '.json', 'w+') as f:
            json.dump(json_object, f, indent=4)


if __name__ == '__main__':
    h = HParser('raw_data_1/2920-h/2920-h.htm')
