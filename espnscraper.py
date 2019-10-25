from selenium import webdriver
import pandas as pd
import numpy as np
import datetime as dt

"""
This is the python 3.6+ implementation of my previous R script. I will eventually re-write that script in RSelenium.
"""

# 1.0 Setting global variables. Schedule url formula, XPath to navigate the tables, and team list

URL = "https://www.espn.com/nba/team/schedule/_/name/{}/season/2020"
XPATH = '/html/body/div[1]/div/div/div/div/div[5]/div[2]/div[5]/div[1]/div[1]/article/div/section/section/section/table' \
        '/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/div/table/tbody//td'

TEAMS = [
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM", "MIA",
    "MIL", "MIN", "NOR", "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTH", "WAS"
]


def build_sched_url(team, url_form=URL):
    return url_form.format(team)


def date_process(data):
    """
    Processes ESPN's thankfully formulaic schedule.
    :param data: Selenium data. Schedule data from espn.
    :return: np.array. Array of dates
    """
    date_results = []
    for i, el in enumerate(data):
        try:
            d = dt.datetime.strptime(el.text + " 2020", "%a, %b %d %Y")
            if d.month > 6:
                d = d.replace(year=2019)
            date_results.append(d)
        except ValueError:
            pass
    return np.array(date_results)


def fetch_team(driver, dest):
    """
    Retrieves dates for one team from one schedule URL.
    :param driver: webdriver. Selenium browser.
    :param dest: str. Url to navigate to.
    :return: np.array. Array of dates
    """
    # 2.5
    driver.get(dest)
    # 2.6
    elem = driver.find_elements_by_xpath(XPATH)
    # 2.7
    return date_process(elem)


def create_schedule_vector(date_df):
    # 3.2 There is definitely a less dumb way to accomplish this section than to send to pandas and pull from numpy,
    # but whatever
    date_values = date_df.values
    daily = np.sum(date_values, 1) / 2
    conflicted = np.sum(date_values * daily[:, None], 0)
    vector = pd.Series(conflicted / conflicted.mean(), index=date_df.columns)
    vector.to_csv('schedule_vector.csv', header=True)


def create_conflict_matrix(date_df):
    date_values = date_df.values
    # 4.0 Building the team x team chart
    team_matrix = np.zeros([30,30])
    # Is there a smarter way to iterate this?
    for i in range(date_values.shape[1] - 1):
        # 4.1 Pulls one team
        primary = date_values[:, i]
        for j in range(1, date_values.shape[1]):
            # 4.2 Calculates conflicts with other teams
            cons = (primary * (primary == date_values[:, j]))
            team_matrix[i, j] = cons.sum() % 82
            team_matrix[j, i] = cons.sum() % 82
    frame = pd.DataFrame(team_matrix, index=date_df.columns, columns=date_df.columns, dtype=int)
    frame.to_csv('schedule_frame.csv')


def create_playoff_score(date_df):
    x = pd.Series(date_df.index)
    w = np.floor(x / 7 + 2)
    y = 1 - 1 / w
    team_vec = date_df.multiply(y, axis='index').sum(axis=0)
    scaled_vec = 2 * (team_vec - team_vec.mean())
    scaled_vec.sort_values().to_csv('playoff_score.csv', header=True)


def get_date_vectors():
    """
    Grabs the dates of very game for every team
    :return dict: All team information
                  'teams': Each team with every game date
                  'dates': Full list of unique game dates
    """
    # 2.0
    # 2.1 Start up the Selenium driver
    driver = webdriver.Chrome()

    # 2.2 Set up output
    team_dict = {}
    all_dates = np.array([])

    for team in TEAMS:
        # 2.3
        url = build_sched_url(team)
        # 2.4
        team_dates = fetch_team(driver, url)
        # 2. 8
        all_dates = np.append(all_dates, team_dates)
        team_dict.update({team: team_dates})
    driver.close()
    # 2.9
    final_dates = np.sort(np.unique(all_dates))
    return {'dates': final_dates, 'teams': team_dict}


def build_conflict_metrics():
    data = get_date_vectors()
    # 3.0 Calculating each team's score
    final_dates = data['dates']
    team_dict = data['teams']
    # 3.1 Builds a date-vector for each team
    table_dict = {team: np.isin(final_dates, dates).astype(int) for team, dates in team_dict.items()}
    date_table = pd.DataFrame.from_dict(table_dict)
    create_schedule_vector(date_table)
    create_conflict_matrix(date_table)
    create_playoff_score(date_table)


if __name__ == '__main__':
    build_conflict_metrics()
