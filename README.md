# **NFL Players Tweet/Performance Analysis**

## Project Description

### Background

The integration of online data, such as NFL players' tweets and game statistics, provides a potentially useful approach to predicting performance and understanding game outcomes. By analyzing tweet sentiment, behavioral patterns, and public reactions, people can uncover correlations between players' mental states and on-field results, which can include factors influencing performance, such as focus, confidence, or distractions. Machine learning models enhance this analysis by identifying patterns and generating predictions based on both statistical and textual data with sentiment text-analysis.

### Problem

The performance of NFL players seems random or too complex to predict.

### Solution

Use NFL player tweets and data derived from those tweets to establish a relationship between performance and what NFL players are saying online.

### Applications

- Sports betting/fantasy football
- Understanding the relationship between mental state and performance in professional sports

## Dataset

All of the data is **scraped**.

- https://www.pro-football-reference.com/friv/nfl-player-twitter.htm
    - A key-value-pair list of NFL player names and their twitter handle
- https://www.footballdb.com
    - A website that displays NFL player stats per-game
- https://x.com
    - A social media website that displays NFL player tweets

### Scraping Methods

**https://www.pro-football-reference.com/friv/nfl-player-twitter.htm**
- BeautifulSoup with HTML Parser to store table of NFL player names with a link to their twitter profile

**https://www.footballdb.com**
- BeautifulSoup with HTML Parser to store table of NFL player stats per-game
- Uses the NFL player names from the previous dataset to get stats for only the players that have a twitter profile

**https://x.com**
- Selenium Chrome Webdriver to store table of NFL player tweets
- Uses intersection of NFL players from first two datasets to get tweets for only the players that have stats and tweets

### Scraping Complications

- https://www.pro-football-reference.com/friv/nfl-player-twitter.htm
    - This dataset already includes a link to a webpage for the player which includes the desired data
        - Unfortunately, https://www.pro-football-reference.com limits basic HTTP requests, meaning traditional web scraping isn't an option
- https://x.com
    - Twitter has an API, but for free access, it's limited to 100 post reads per day, and higher tiers cost a minimum of over $200 a month
    - Twitter also has restrictions for how much content can be loaded, so only a few hundred posts can be extracted before a ~10 minute timeout occurs where no posts are loaded

### Purpose

The heart of the datasets and project is the NFL player-twitter handle mapping webpage. This data provides the base relationship between player performance and tweets. From this relationship, the other 2 datasets can be extracted and connected.

**Independent Variable:** NFL player tweets

**Dependent Variable:** NFL player performance

## Project Details

### Usage of Datasets

The relationship between performance and tweets will be established using different strategies. Then, analysis using different data representation methods will be used to create predictions with accuracy-based scoring to alleviate the perceived complexity and randomness of NFL player performance.

## References (relevant works)

"Data-Driven Prediction of Athletes’ Performance Based on Their Social Media Presence": This research analyzed millions of tweets from NBA players to derive features reflecting mood, social media behavior, and sleep quality before games. The study found that the number of tweets a player is tagged in prior to a game significantly improves the accuracy of performance predictions. 
[Springer Nature Link](https://link.springer.com/chapter/10.1007/978-3-031-18840-4_15)

"Performance Prediction of Basketball Players Using Automated Personality Mining with Twitter Data": This study utilized Twitter data to mine personality traits of basketball players and predict their NBA performance. It concluded that certain personality traits, such as extraversion, agreeableness, and conscientiousness, correlate with basketball performance and can be used, alongside previous game statistics, to predict future performance. 
[Emerald Insight](https://www.emerald.com/insight/content/doi/10.1108/sbm-10-2021-0119/full/html)

"Prediction from Regional Angst – A Study of NFL Sentiment in Twitter Data": This research applied financial stock market techniques to sentiment gathered from social media to predict NFL game outcomes. The analysis revealed that sentiment-based wagers yielded higher average returns compared to an odds-only approach, indicating a significant relationship between social media sentiment and game performance. 
[Rob Schumaker](https://robschumaker.com/publications/DSS%20-%20Prediction%20from%20Regional%20Angst.pdf)