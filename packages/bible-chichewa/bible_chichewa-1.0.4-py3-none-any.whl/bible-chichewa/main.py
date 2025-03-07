# author: M2K Developments
# github: https://github.com/m2kdevelopments

import json
import os

"""
Get Bible information
"""
class Bible:

    def __init__(self):
        # Get the current working directory
        self.current_directory = os.getcwd()

    def getBooks(self):
        """
        Get the names of all books in the Bible.

        :return: A list of Bible book names.
        """
        relative_path = "src\\content\\books.json"
        absolute_path = os.path.join(self.current_directory, relative_path)

        with open(absolute_path, "r") as json_file:
            books = json.load(json_file)
            return list(map(lambda book: book['name'], books))

    def getChapter(self, book: int, chapter: int):
        """
        Get the verses of a specific chapter from a book in the Bible.

        :param book: The index of the Bible book (1-based).
        :param chapter: The chapter number.
        :return: A dictionary containing the chapter's verses.
        """
        relative_path = f"src\\resources\\{book}\\{chapter}.json"
        absolute_path = os.path.join(self.current_directory, relative_path)

        with open(absolute_path, "r") as json_file:
            verses = json.load(json_file)
            return verses

    def getVerse(self, book: int, chapter: int, verse: int):
        """
        Get the content of a specific verse from a chapter in a book of the Bible.

        :param book: The index of the Bible book (1-based).
        :param chapter: The chapter number.
        :param verse: The verse number.
        :return: The content of the specified verse.
        """
        return self.getChapter(book, chapter)[verse]

    def getVerses(self, book, chapter: int, verseStart: int, verseEnd: int):
        """
        Get a range of verses from a chapter in a book of the Bible.

        :param book: The index of the Bible book (1-based).
        :param chapter: The chapter number.
        :param verseStart: The starting verse number.
        :param verseEnd: The ending verse number.
        :return: A list containing the verses within the specified range.
        """
        return self.getChapter(book, chapter)[verseStart-1:verseEnd]

    def getChapterCount(self, book: int):
        """
        Get the number of chapters in a specific book of the Bible.

        :param book: The index of the Bible book (1-based).
        :return: The number of chapters in the book.
        """
        relative_path = "src\\content\\books.json"
        absolute_path = os.path.join(self.current_directory, relative_path)

        with open(absolute_path, "r") as json_file:
            books = json.load(json_file)
            return list(map(lambda book: book['chapters'], books))[book-1]

    def getVerseCount(self, book: int, chapter: int):
        """
        Get the number of verses in a specific chapter of a book in the Bible.

        :param book: The index of the Bible book (1-based).
        :param chapter: The chapter number.
        :return: The number of verses in the chapter.
        """
        return len(self.getChapter(book, chapter))