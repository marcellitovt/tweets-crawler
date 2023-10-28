from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tabulate import tabulate
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

# Setup the tweet page
def setup():
  driver = webdriver.Chrome()
  token = "238gNj4NeBpz4LfBgVzOLqXJ6yFfsMtT"

  driver.get("https://www.instagram.com") # Open tweet page
  driver.add_cookie({ # Bypass login with cookie auth_token
            'name': "csrftoken",
            'value': token,
            'domain': "www.instagram.com",
            'path': "/",
            'expires': -1,
            'httpOnly': True,
            'secure': True,
            'sameSite': "Strict",
          })
  ## Uncomment this to use advance search
  #driver.get("https://twitter.com/search-advanced?f=live")
  driver.get("https://www.instagram.com")
  
  return driver

# Fill the search form
def search(currentDriver,keyword):
  inputContext = currentDriver.find_element(By.XPATH, "//input[@placeholder='Search Twitter']")
  inputContext.clear()
  inputContext.send_keys(keyword)
  inputContext.send_keys(Keys.RETURN)

  current_url = currentDriver.current_url
  currentDriver.get(current_url+"&f=live")

  return currentDriver

def dataCrawler(currentPage, limit_tweets):
    tweet_links = []
    created_ats = []
    usernames = []
    full_texts = []
    langs = []
    replys = []
    retweets = []
    likes = []
    views = []

    previous_count = 0
    same_count_duration = 0

    while len(tweet_links) < int(limit_tweets):

        # Setup BS and find the divs
        page_source = currentPage.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        divs = soup.find_all('div', class_="css-1dbjc4n r-1igl3o0 r-qklmqi r-1adg3ll r-1ny4l3l")

        # Start Crawling
        for div in divs:
            ## Link
            link_ele = div.find("a", class_="css-4rbku5 css-18t94o4 css-901oao r-1bwzh9t r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0")
            try:
              base = "https://twitter.com"
              link = link_ele.get("href")
              if base + link not in tweet_links:
                  tweet_links.append(base + link)

                  ## Username
                  username = re.search(r"/([^/]+)/status", link).group(1)
                  usernames.append(username)

                  ## full_text
                  try:
                    ele_fulltext = div.find("div", class_="css-901oao r-1nao33i r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0")
                    text  = ele_fulltext.getText()
                    full_texts.append(text)
                  except:
                    full_texts.append("")

                  ## Created_at
                  try:
                    ele_time = div.find("time")
                    created_at  = ele_time.get("datetime")
                    datetime_obj = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    created_ats.append(datetime_obj)
                  except:
                    created_ats.append("")

                  ## lang
                  try:
                    ele_lang = div.find("div", class_="css-901oao r-1nao33i r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0")
                    lang  = ele_lang.get("lang")
                    langs.append(lang)
                  except: 
                    langs.append("")

                  #[0] Reply
                  #[1] Retweets
                  #[2] Likes
                  #[3] Views
                  ## Tweets interaction
                  try:
                    ele_interactions = div.find("div", class_="css-1dbjc4n r-1ta3fxp r-18u37iz r-1wtj0ep r-1s2bzr4 r-1mdbhws")
                    interactions = ele_interactions.find_all("div", class_="css-18t94o4 css-1dbjc4n r-1777fci r-bt1l66 r-1ny4l3l r-bztko3 r-lrvibr")

                    reply = interactions[0].get("aria-label")
                    reply = re.search(r'\d+', reply)[0]
                    replys.append(reply)

                    retweet = interactions[1].get("aria-label")
                    retweet = re.search(r'\d+', retweet)[0]
                    retweets.append(retweet)

                    like = interactions[2].get("aria-label")
                    like = re.search(r'\d+', like)[0]
                    likes.append(like)

                    view = div.find("a", class_="css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21 r-1777fci r-bt1l66 r-1ny4l3l r-bztko3 r-lrvibr")
                    view = view.get("aria-label")
                    view = re.search(r'\d+', view)[0]
                    views.append(view)
                  except:
                    replys.append("")
                    retweets.append("")
                    likes.append("")
                    views.append("")
                  
            except:
              pass

        print("Total tweets saved " + str(len(tweet_links)))

        # Check if tweet_links count remains the same
        current_count = len(tweet_links)
        if current_count == previous_count:
            same_count_duration += 1
        else:
            same_count_duration = 0
            previous_count = current_count

        # Break the loop if the count remains the same for 5 seconds
        if same_count_duration == 5:
            print("No more tweets, Terminating...")
            break

        # Scroll by pressing the arrow-down key
        for _ in range(30):
            currentPage.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
    print("Length of tweet_links:", len(tweet_links))
    print("Length of created_ats:", len(created_ats))
    print("Length of usernames:", len(usernames))
    print("Length of full_texts:", len(full_texts))
    print("Length of langs:", len(langs))
    print("Length of replys:", len(replys))
    print("Length of retweets:", len(retweets))
    print("Length of likes:", len(likes))
    print("Length of views:", len(views))
    data = {"tweet_links": tweet_links,"created_at":created_ats, "usernames": usernames, "full_text" : full_texts, "language" : langs, "reply" : replys,
            "retweet": retweets, "like" : likes, "view" : views}
    return data

keyword = input("Input your search keyword.. \n")
#keyword = "Tamsis since:2023-06-02 until:2023-06-07" # Use the time limit
limit = input("How many tweets you want to get?.. \n")

# Counting 
start_time = time.time()

browser = setup()
# page = search(browser, keyword)
# data = dataCrawler(page, limit)

# Create a DataFrame from the dictionary
# df = pd.DataFrame(data)

# filename = input("Input File Names.. \n")
# Export the DataFrame to a CSV file
# df.to_csv("output/"+ filename +"-tweets.csv", index=False, mode="w")

# print ("Program took", time.time() - start_time, "seconds to run")




#Pause
input("Press any key to close..")
browser.quit()
