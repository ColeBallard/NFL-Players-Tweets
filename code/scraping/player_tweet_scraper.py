import os
from time import sleep
import random

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from player_scraper import PlayerScraper
import utilities as u


class PlayerTweetScraper(PlayerScraper):
    def __init__(self):
        # Get the absolute path to the .env file in the root directory
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        env_path = os.path.join(root_dir, ".env")

        # Load the .env file
        load_dotenv(env_path)

        super().__init__(
            scraper_type='PLAYER_TWEET',
            refreshFunc=self.getNflPlayerTweets
        )

        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                        ' Chrome/70.0.3538.77 Safari/537.36'
        }

        # 2006 is the year twitter was founded
        self.EARLIEST_YEAR = 2006

    def getNflPlayerTweets(self):
        player_handles = self.csvToTable('PLAYER_HANDLE')
        player_stats = self.csvToTable('PLAYER_STAT')

        valid_player_handles = self._getValidNflPlayerHandles(player_handles=player_handles, player_stats=player_stats)

        data = {
            "headers": ['player_handle', 'text', 'date', 'is_repost'],
            "data": []
        }

        twitter_login_url = 'https://x.com/i/flow/login?lang=en'

        # Construct the relative path to the ChromeDriver executable
        driver_path = os.path.join(os.path.dirname(__file__), "..", "res", "chromedriver-win64", "chromedriver.exe")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service)

        try:
            # Open the login page
            driver.get(twitter_login_url)

            self._loginToTwitter(driver=driver)

            # Check if the "Close" button exists
            close_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="app-bar-close"]')

            # If the button exists, click it
            if close_buttons:
                close_buttons[0].click()

            # Extract the `twitter_profile` column
            twitter_profiles = [row['twitter_profile'] for row in valid_player_handles['data'] if 'twitter_profile' in row]

            # Now you can loop through `twitter_profiles` and use it as the list of webpages
            for twitter_url in twitter_profiles:
                if u.isValidTwitterHandle(twitter_url):
                    retry_counter = 0

                    while True:
                        try:
                            sleep(random.uniform(2, 6))

                            driver.get(twitter_url)

                            player_tweets = self._getTweets(driver=driver, twitter_url=twitter_url)

                            # Check if `player_tweets` is not empty
                            if player_tweets:
                                for tweet in player_tweets:
                                    data['data'].append(tweet)  # Append each tweet dictionary individually
                            
                            break
                        except Exception as e:
                            retry_counter += 1
                            if retry_counter <= 3:
                                sleep_time = 720 + random.uniform(1, 300)
                                print(f'Error while getting tweets from {twitter_url}: {e}. Retrying ({retry_counter}/3) in {sleep_time} seconds.')
                                sleep(sleep_time)
                            else:
                                print(f'Error while getting tweets from {twitter_url}: {e}. Max retried reached. Skipping...')
                                break
        except Exception as e:
            print(f"An error occurred: {e}")
        
        finally:
            # Close the browser
            driver.quit()

            return data

    def _loginToTwitter(self, driver):
        # Log in
        # Wait for the input field with autocomplete="username"
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
        )

        # Enter the username
        username_field.send_keys(os.getenv("TWITTER_USER"))

        # Wait for the "Next" button with visible text and click it
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Next"]]'))
        )
        next_button.click()

        # Wait for the password input field to be visible and enter the password
        password_field = WebDriverWait(driver, 120).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="current-password"]'))
        )
        password_field.send_keys(os.getenv("TWITTER_PASS"))

        
        # Wait for the "Log in" button with visible text and click it
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[.//span[text()="Log in"]]'))
        )
        login_button.click()

        print("Login successful!")

    def _getValidNflPlayerHandles(self, player_handles, player_stats):
        # Extract the player names from the second table (case-insensitive matching)
        filtered_player_stats = set(row["Player_Name"].strip().lower() for row in player_stats["data"])

        # Filter the first table rows based on existence in the second table
        filtered_data = [
            row for row in player_handles["data"]
            if row["player_name"].strip().lower() in filtered_player_stats
        ]

        # Return the new dictionary with the headers and filtered data
        return {
            "headers": player_handles["headers"],
            "data": filtered_data
        }
    
    def _getTweets(self, driver, twitter_url):
        tweets_data = []
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0

        print(f"Starting to scrape tweets from: {twitter_url}")

        try:
            print("Waiting for tweets to be present on the page...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
            )
            print("Tweets are now present on the page.")
        except Exception as e:
            raise Exception(e)

        while True:
            tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
            num_tweets = len(tweets)
            print(f"Number of tweets found: {num_tweets}")

            for index, tweet in enumerate(tweets):
                # Extract the tweet text
                try:
                    tweet_text_element = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                    tweet_text = tweet_text_element.text
                except Exception as e:
                    tweet_text = None
                    print(f"Error extracting tweet text: {e}")

                # Extract the date
                try:
                    date_element = tweet.find_element(By.TAG_NAME, 'time')
                    tweet_date = date_element.get_attribute('datetime')
                except Exception as e:
                    tweet_date = None
                    print(f"Error extracting tweet date: {e}")

                # Check if the tweet is a repost
                is_repost = False
                try:
                    social_context = tweet.find_element(By.CSS_SELECTOR, 'span[data-testid="socialContext"]')
                    if "reposted" in social_context.text.lower():
                        is_repost = True
                except NoSuchElementException:
                    pass
                except Exception as e:
                    print(f"Unexpected error checking if tweet is a repost: {e}")

                # Avoid adding duplicate tweets
                if not any(t['text'] == tweet_text and t['date'] == tweet_date for t in tweets_data):
                    if tweet_text:
                        tweet_text = tweet_text.replace('\n', ' ').replace('\r', ' ')
                    tweets_data.append({
                        'player_handle': twitter_url,
                        'text': tweet_text,
                        'date': tweet_date,
                        'is_repost': is_repost
                    })
                else:
                    print("Duplicate tweet found. Skipping.")

            # Before scrolling, get the last tweet
            last_tweet = tweets[-1]

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep_time = random.uniform(3, 5)
            sleep(sleep_time)

            # Wait until the last tweet is no longer attached to the DOM
            try:
                WebDriverWait(driver, 8).until(
                    EC.staleness_of(last_tweet)
                )
            except Exception as e:
                print(f"Error waiting for new tweets: {e}")
                break

            # Check if the page height changed
            new_height = driver.execute_script("return document.body.scrollHeight")
            print(f"New page height: {new_height}")

            if new_height == last_height:
                scroll_attempts += 1
                if scroll_attempts >= 3:
                    print("No more tweets to load after multiple attempts.")
                    break
            else:
                scroll_attempts = 0
                last_height = new_height

        print("\nFinished scraping tweets.")
        return tweets_data

