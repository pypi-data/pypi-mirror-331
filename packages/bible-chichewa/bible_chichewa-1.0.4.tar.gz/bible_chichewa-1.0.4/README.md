# Chichewa Bible for Python

![Static Badge](https://img.shields.io/badge/m2kdevelopments-purple?style=plastic&logo=github&logoColor=purple&label=developer&link=https%3A%2F%2Fgithub.com%2Fm2kdevelopments)
![Static Badge](https://img.shields.io/badge/MIT-green?style=plastic&logo=license&logoColor=green&label=license)
![Static Badge](https://img.shields.io/badge/buy_me_a_coffee-yellow?style=plastic&logo=buymeacoffee&logoColor=yellow&label=support&link=https%3A%2F%2Fwww.buymeacoffee.com%2Fm2kdevelopments)
![Static Badge](https://img.shields.io/badge/paypal-blue?style=plastic&logo=paypal&logoColor=blue&label=support&link=https%3A%2F%2Fpaypal.me%2Fm2kdevelopment)



Chichewa Bible pip package: Access and integrate the Chichewa translation of the Bible into your python applications with ease. Simplify verse retrieval, text search, and more using this lightweight and versatile pip package.


## Features

- Access verses, chapters, and books of the Chichewa Bible programmatically.
- Retrieve text content in Chichewa for quoting, referencing, and display.
- Flexible search functionality for finding specific passages or keywords.
- Lightweight and easy-to-use API for seamless integration into Node.js applications.
- Continuously updated to reflect the latest versions of the Chichewa Bible text.

## Installation

You can install the Chichewa Bible python package using pip:

```
pip install bible-chichewa
```

## Examples
To use the bible-chichewa library to retrieve a verse from the Chichewa Bible, follow these steps:

### Example: Retrieving a Bible Verse
```
bible = Bible()
books = bible.getBooks()
print(f"There are {len(books)} books in the bible")

bookNumber = 1  # Genesis
book = books[bookNumber-1]
chapter = 1
verse = 1

verseText = bible.getVerse(bookNumber, chapter, verse)
print(f"{book} {chapter}:{verse}: {verseText}")
```


### Example: Retrieving a Bible Chapter

```
bible = Bible()
books = bible.getBooks()
bookNumber = 1  # Genesis
book = books[bookNumber-1]

chapter = 1 

chapterVerses = bible.getChapter(bookNumber, chapter)

print(f"Chapter {book} {chapter}:")
for i in range(0, len(chapterVerses)):
    verse = i+1
    print(f"{verse}. {chapterVerses[i]}\n")

```

### Example: Retrieving a Bible Verses within Range
```
bible = Bible()

books = bible.getBooks()
bookNumber = 2 ## Exodus
book = books[bookNumber-1]

chapter = 20
verseStart = 1
verseEnd = 5

verses = bible.getVerses(bookNumber, chapter, verseStart, verseEnd)

print(f"{book} {chapter}:{verseStart}-{verseEnd}:")
for index in range(0, len(verses)):
    verse = verses[index]
    print(f"{verseStart + index}: {verse}\n")

```

<a href="https://www.buymeacoffee.com/m2kdevelopments" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !importantwidth: 217px !important" >
</a>