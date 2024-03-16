import json
import os


class bookManager:
    def __init__(self, rootPath):
        self.rootPath = rootPath
        self.bookList = self.__getAllBooks()

    def __createBookTree(self):
        books = []
        err_File = []
        for bookPath in self.bookList:
            book = {}
            bookConfigFile = self.__getBookConfig(bookPath)
            editor_identifier = None
            try:
                with open(f'{self.rootPath}/{bookPath}/{bookConfigFile}', 'r', encoding='utf-8') as f:
                    bookConfig = json.load(f)
                    editor_identifier = bookConfig['editor_identifier']
            except:
                err_File.append(f'{self.rootPath}/{bookPath}/{bookConfigFile}')
                continue
            book['editor_identifier'] = f"{editor_identifier} - {bookConfigFile}"
            book['category'] = []
            categoryList = os.listdir(f"{self.rootPath}/{bookPath}/category")
            for category in categoryList:
                if category.endswith('.json'):
                    try:
                        with open(f'{self.rootPath}/{bookPath}/category/{category}', 'r', encoding='utf-8') as f:
                            categoryConfig = json.load(f)
                            book['category'].append(
                                (category, categoryConfig['title'] if 'title' in categoryConfig else "null"))
                    except:
                        err_File.append(f'{self.rootPath}/{bookPath}/category/{category}')
            book['entry'] = []
            entryList = os.listdir(f"{self.rootPath}/{bookPath}/entry")
            for entry in entryList:
                if entry.endswith('.json'):
                    try:
                        with open(f'{self.rootPath}/{bookPath}/entry/{entry}', 'r', encoding='utf-8') as f:
                            categoryConfig = json.load(f)
                            book['entry'].append(
                                (entry,
                                 categoryConfig['title'] if 'title' in categoryConfig else "null",
                                 categoryConfig['parent'] if 'parent' in categoryConfig else "null"))
                    except:
                        err_File.append(f'{self.rootPath}/{bookPath}/entry/{entry}')
            books.append(book)
        return books, err_File

    def __getAllBooks(self):
        return os.listdir(self.rootPath)

    def __getBookConfig(self, bookPath):
        fileList = os.listdir(f"{self.rootPath}/{bookPath}")
        return [config for config in fileList if config.endswith('.json')][0]

    def get(self):
        return self.__createBookTree()
