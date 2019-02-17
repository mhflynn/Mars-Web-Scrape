###############################################################################
#
# ## Mission to Mars
#
###############################################################################

from splinter import Browser
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import time

###############################################################################
#Create Browser object
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', **executable_path, headless=True)

###############################################################################
# ### Scrape the NASA Mars news site for latest article

def scrape_mars() :
        # Open the news page for NASA Mars site, use BeautifulSoup to parse the HTML
        print('Scrape Mars news ...')

        url = 'https://mars.nasa.gov/news/'
        browser.visit(url)
        time.sleep(3)  # Sometimes wrong html is captured, sleep seems to help

        soup = bs(browser.html, 'html.parser')

        # From inspection of the HTML using browser developer tools, the news articles are
        # in a list, within the <section> tag of class type "grid_gallery". Each list item has
        # a <div> tag of class type "list_text", within which the article title and description 
        # can be extracted from <div> tags of class "content_title" and "article_teaser_body", 
        # respectively. Since request is for the latest/first article in the list, use find
        # method to get the first one.

        news = soup.find("section", class_="grid_gallery").find("div", class_="list_text")
        news_title = news.find('div', class_='content_title').text
        news_p = news.find('div', class_='article_teaser_body').text
        #print (news_title, "\n", news_p)

        ###############################################################################
        # ### JPL Mars Featured Image Scrape
        print('Scrape Mars featured image ...')

        jpl_url = "https://www.jpl.nasa.gov"
        query = "/spaceimages/?search=&category=Mars"
        browser.visit(jpl_url+query)

        jpl_soup = bs(browser.html, 'html.parser')
        featured_image_url = jpl_url+jpl_soup.find('a', id='full_image')['data-fancybox-href']
        featured_image_url

        ###############################################################################
        # ### Mars Weather Scrape
        print('Scrape Mars weather ...')

        tw_url = "https://twitter.com/marswxreport?lang=en"
        browser.visit(tw_url)

        tw_soup = bs(browser.html, 'html.parser')

        # Loop through the tweets to find weather report
        for t in tw_soup.find_all('p', class_='tweet-text') :
                if t.text.startswith("Sol") :
                        mars_weather = t.text
                        break

        # Remove extraneous text as end of the weather text
        mars_weather.find('pic.twitter')
        mars_weather = mars_weather[0:mars_weather.find('pic.twitter')]

        ###############################################################################
        # ### Mars Facts Scrape
        print('Scrape Mars facts ...')

        # Use pandas to extract table data from space-facts page
        facts_url = 'https://space-facts.com/mars/'
        tables = pd.read_html(facts_url)

        # Format the table for bootstrap

        table_soup = bs(tables[0].to_html(header=False, index=False), 'html.parser')

        table_soup.table['class']='table table-sm table-bordered small'

        del table_soup.table['border']

        for tag in table_soup.table.tbody.find_all('tr') :
                tag.td['scope'] = 'row'
                tag.td.name = 'th'

        facts = str(table_soup)

        ###############################################################################
        # ### Mars Hemispheres Scrape
        print('Scrape Mars hemisphere images ..')

        hemi_url = "https://astrogeology.usgs.gov"
        hemi_query = "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
        browser.visit(hemi_url+hemi_query)

        hemi_soup = bs(browser.html, 'html.parser')

        # Get image titles
        hemi_map = []
        for h in hemi_soup.find_all('div', class_="description") :
                hemi_map.append({'title':h.find('a').text})

        # Get image urls
        for hmp in hemi_map :
                browser.visit(hemi_url+hemi_query)
                browser.click_link_by_partial_text(hmp['title'])
                
                link_soup = bs(browser.html, 'html.parser')
                url = link_soup.find('img', class_='wide-image')['src']
                hmp['img_url'] = hemi_url+url
                print(url)

        # Return scraped data as dictionary
        scrape_d = {'news': {'title':news_title, 'news':news_p},
                'feature_img':featured_image_url,
                'facts': facts,
                'weather':mars_weather,
                'hemi_map':hemi_map
                }
        return scrape_d


###############################################################################
# ### Insert scraped date into Mongo database [Test Code] 
# 
import sys
from pymongo import MongoClient
from pymongo import errors as pymerr

def scrape_to_db (db_doc) :
        client = MongoClient('mongodb://localhost:27017')
        db = client.mars_data

        try :
            db.mars_info.replace_one({}, db_doc, upsert=True)
            
        except pymerr.ServerSelectionTimeoutError :
            print('Scape Test : No database connection found')


if __name__ == "__main__":
    data = scrape_mars()
    if len(sys.argv) >= 2 :
            print ('Database Operation')
            scrape_to_db (data)
