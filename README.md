# NBA Schedule Scraper
This is a project I made to scrape the NBA schedule and provide some metrics about it. I am currently looking to improve these metrics, and any contributions and advice are welcome.

The R version of this project is currently defunct. I will eventually revive it.

## Getting Started
All of the requirements are in the `requirements.frozen` file. You can install them by running `pip install -r requirements.frozen` in the command line.

## Executing
The script doesn't require much. It just dumps the two files in the working directory. Simply run `python3 espnscraper.py`. It should go through pretty quickly.

## Tech
I use Selenium, with a Firefox driver to scrape ESPN's site. The site used to use basic HTML tables, that's why I had the R script which was muuuch faster.

It goes through every team's page since each of them are formulaicly laid out. I then use numpy to process the data, and pandas to export everything.

TODO: Change line 34 to a try-catch in case they change the site again
TODO: Add pathspecs
