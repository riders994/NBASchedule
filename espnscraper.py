from selenium import webdriver
import pandas as pd
import numpy as np

URL = "https://www.espn.com/nba/team/schedule/_/name/{}/season/2020"
XPATH = '/html/body/div[1]/div/div/div/div/div[5]/div[2]/div[5]/div[1]/div[1]/article/div/section/section/section/table/tbody/tr/td/div/div/div[2]/table/tbody/tr/td/div/table/tbody//td'

TEAMS = [
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM", "MIA",
    "MIL", "MIN", "NOR", "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTH", "WAS"
]


def build_sched_url(team, url_form=URL):
    return url_form.format(team)


def date_process(data):
    date_results = []
    for i, el in enumerate(data):
        if i and not (i % 5):
            d = dt.datetime.strptime(el.text + " 2020", "%a, %b %d %Y")
            if d.month > 6:
                d = d.replace(year = 2019)
            date_results.append(d)
    return np.array(date_results)

def fetch_team(driver, dest):
    driver.get(dest)
    elem = driver.find_elements_by_xpath(XPATH)
    return date_process(elem)


def get_date_vectors():
    driver = webdriver.Firefox()
    team_dict = {}
    all_dates = np.array([])
    for team in TEAMS:
        url = build_sched_url(team)
        team_dates = fetch_team(driver, url)
        all_dates = np.append(all_dates, team_dates)
        team_dict.update({team: team_dates})
    driver.close()
    final_dates = np.sort(np.unique(all_dates))
    return {'dates': final_dates, 'teams': team_dict}


def build_conflict_metrics():
    data = get_date_vectors()
    final_dates = data['dates']
    team_dict = data['teams']
    table_dict = {team: np.isin(final_dates, dates).astype(int) for team, dates in team_dict.items()}
    date_table = pd.DataFrame.from_dict(table_dict)
    date_values = date_table.values
    daily = np.sum(date_values, 1)/2
    conflicted = np.sum(date_values * daily[:, None], 0)
    vector = pd.Series(conflicted/conflicted.mean(), index = date_table.columns)
    vector.to_csv('schedule_vector.csv')
    for i in range(date_values.shape[1] - 1):
        for j in range(1, date_values.shape[1]):
            primary = date_values[:,i]
            cons = (primary * (primary == date_values[:,j]))
            team_matrix[i, j] = cons.sum() % 82
            team_matrix[j,i] = cons.sum() % 82
    frame = pd.DataFrame(team_matrix, index=date_table.columns, columns=date_table.columns, dtype=int)
    frame.to_csv('schedule_frame.csv')