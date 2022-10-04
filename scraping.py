# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime as dt

# Set up Splinter
def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()

    return data

# Scrape Mars News
def mars_news(browser):

    # Visit the mars nasa news site
    # url = 'https://redplanetscience.com'
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first `div` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):

    # Visit URL
    # url = 'https://spaceimages-mars.com'
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    #img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    
    return img_url

# ## Mars Facts
def mars_facts():

    # The Pandas function read_html() specifically searches for and returns a list of 
    # tables found in the HTML.

    try:
        # use 'read_html' to scrape the facts table into a dataframe
        # df = pd.read_html('https://galaxyfacts-mars.com')[0]
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None
    
    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe to HTML format, add bootstrap
    return df.to_html()

# Scrape the url to each image of each hemisphere with it's title.
# Return the hemispheres in list of dictionaries.
def mars_hemispheres(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'

    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Convert the browser html to a soup object
    html = browser.html

    title_soup = soup(html, 'html.parser')

    # Titles are on the first page so get them first using the 'h3' tag.
    # The parent of each title element will be used to get the html page for the image.
    title_elems = title_soup.find_all('h3')

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for title_elem in title_elems:
        
        # If title == 'Back' we are done with the list of titles.
        # Alternatively, we could use the parent to get the last href = '#'
        # We also need to skip elements that have blank titles.
        if title_elem.text == 'Back':
            break
        elif title_elem.text == '':
            continue

        # Get the html page to visit in order to find the image
        image_url = title_elem.parent['href']
        
        # Save the title
        image_title = title_elem.text

        # Get the full path to the html page
        image_url = f"{url}{image_url}"
        
        # Go to the url where the image info is located:
        browser.visit(image_url)
        
        # Convert the new html page to a soup object
        html = browser.html
        image_soup = soup(html, 'html.parser')

        # Get the 'a' tag where it's text = 'Sample':
        image_url = image_soup.find('a', text='Sample').get('href')

        # Get use the href to get the full url to the enhanced image:
        image_url = f"{url}{image_url}"

        # Create a key value pair in the hemisphere variable:
        hemisphere = {'image-url': image_url, 'title': image_title}

        # Add the hemisphere to the list of hemispheres:
        hemisphere_image_urls.append(hemisphere)

        # Navigate back to the beginning to get the next hemisphere title and image.
        browser.back()
   
    # 4. Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
