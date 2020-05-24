import json
import os


class TParser:
    def __init__(self, book_path):
        self.book_path = book_path
        self.book_text = []
        self.paragraph_block = []
        self.copy_text()
        # self.fetch_info()
        self.split_chapter(82, 3852)
        self.store_chapter("")

    def copy_text(self):
        with open(self.book_path, encoding='UTF-8') as f:
            for line in f:
                self.book_text.append(line)

    def fetch_info(self):
        # Parse the title, author, translator, release date
        for line in self.book_text:
            if line.startswith('Title:'):
                print(line)
            elif line.startswith('Author:'):
                print(line)
            elif line.startswith('Release Date:'):
                print(line)
            elif line.startswith('Translator:'):
                print(line)

    def split_chapter(self, start_index, end_index):
        # Split the chapter to paragraphs between book_text[start_index: end_index]
        self.paragraph_block = []
        paragraph = ''
        for i in range(start_index, end_index):
            if self.book_text[i] != '\n':
                paragraph += self.book_text[i]
            else:
                if paragraph != '':
                    self.paragraph_block.append(paragraph)
                    paragraph = ''
        if paragraph != '':
            self.paragraph_block.append(paragraph)

    def store_chapter(self, name):
        file_name = 'data_1/7971.json'

        with open(file_name, 'r+', encoding='UTF-8') as f:
            data = json.load(f)
            data['content'].append({
                "name": name,
                "sub_name": "",
                "text": self.paragraph_block
            })
            # for chapter in data['content']:
            #     if chapter['name'] == name:
            #         chapter['text'] = self.paragraph_block
            #         break

        os.remove(file_name)

        with open(file_name, 'w', encoding='UTF-8') as f:
            json.dump(data, f, indent=4)


if __name__ == '__main__':
    t = TParser('raw_data_1/7979-8.txt')
