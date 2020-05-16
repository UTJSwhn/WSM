import zipfile
import os

for author_name in os.listdir('books'):
    zip_file_path = 'books/' + author_name
    for file_name in os.listdir(zip_file_path):
        if file_name.endswith('.zip'):
            zip_file = zipfile.ZipFile(zip_file_path + '/' + file_name)
            for names in zip_file.namelist():
                if names.endswith('.txt'):
                    zip_file.extract(names, 'raw_txt')
                else:
                    zip_file.extract(names, 'raw_html')
