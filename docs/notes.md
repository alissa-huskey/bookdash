

Scraping
--------

* [Web Scraping With Lxml](https://timber.io/blog/an-intro-to-web-scraping-with-lxml-and-python/)
* [Web scraping from Wikipedia using Python – A Complete Guide](https://www.geeksforgeeks.org/web-scraping-from-wikipedia-using-python-a-complete-guide/)


Authentication
--------------

* [Posting Data and Using Sessions with Requests](https://kishstats.com/python/2019/03/01/python-requests-posting-data.html)
* [abdulmoizeng/crawlers-demo](https://github.com/abdulmoizeng/crawlers-demo/blob/master/library-example/spider.py)
* [requests > Advanced Usage](https://requests.readthedocs.io/en/master/user/advanced/)
* [How to scrape a website that requires login with Python](https://kazuar.github.io/scraping-tutorial/)


Headless Browsers
-----------------

* [A Practical Introduction to Web Scraping in Python](https://realpython.com/python-web-scraping-practical-introduction/#interact-with-html-forms)
* [Launching a headless browser](https://www.usetrove.io/blog/headless-web-scraping-with-python/)

Goodreads Books Export
----------------------

* URL: https://www.goodreads.com/review/import
* Click: button.gr-form--compact__submitButton
* (wait)
* Click: div#exportFile.fileList a
  <a href="/review_porter/export/538517/goodreads_export.csv">Your export from 12/07/2024 - 02:59</a>


Audible Library Exporter
------------------------

* [Audible Library Downloader](https://github.com/andrebradshaw/audible/blob/master/downloadAudibleLibrary.js)
* [4 Methods to Export Audible Books List](https://www.audiobooksgeek.com/how-to-export-audible-library-list/)
* [Youtube Demo](https://youtu.be/x5cHQs3dxd8)


1. Go to the Audible Library Downloader page and copy the code from the js file.
1. Next, open the Audible website in your internet browser and log in to your account
1. For Windows, press F12 to open the developer tool interface. Mac users can either press Command + Option + I or right-click on the browser page and click Inspect.
1. Make sure you are in the Console tab. Paste the code that you copied and click Enter.

The code will start running and will take anywhere from a couple of minutes to half an hour depending on how many titles you have. For around 400 titles it took 15 minutes.

The export file will have the URL, title, author, narrator, series, main category, subcategory, other categories, duration, release date, release time, and type (fiction/non-fiction).

### Parse .tsv file

```
import csv

with open(tsv) as fp:
    reader = csv.DictReader(fp, dialect=csv.excel_tab)
    audiobooks = list(reader)
```

Google Books API
----------------

* [Google Books API Wrapper (Python)](https://pypi.org/project/google-books-api-wrapper/)
* [Google Books API Docs](https://developers.google.com/books/docs/v1/using)

SQLModel Like Filters
---------------------

* [sqlmodel-filters](https://github.com/ninoseki/sqlmodel-filters)
