# Introduction

This is a simple project I built to scrape data off of french website leboncoin.fr in order to extract local car ads.

There are many projects available that scrape data off of it using combinations of Requests/URLLib and BeautifulSoup libraries. However, leboncoin.fr recently added bots protection with the help of DataDome, and therefore most of these projects have been rendered useless (to my knowledge)

My requirement: Access leboncoin, search for car ad listings for a specific make and model and collect the relevant data into a dataset which can then be manipulated using excel.

To achieve this, I used Selenium library along with the "chromedriver" (downloadable .exe) to drive/manipulate the chrome browser directly, move from page to page and extract the information I need.

Project made using Python 3.7