from sportsipy.nba.schedule import Schedule
import pandas as pd
import numpy as np
import datetime as dt

"""
This is the python 3.6+ implementation of my previous R script. I will eventually re-write that script in RSelenium.
"""


TEAMS = [
    "ATL", "BOS", "BRK", "CHI", "CHO", "CLE", "DAL", "DEN", "DET", "GSW", "HOU", "IND", "LAC", "LAL", "MEM", "MIA",
    "MIL", "MIN", "NOP", "NYK", "OKC", "ORL", "PHI", "PHO", "POR", "SAC", "SAS", "TOR", "UTA", "WAS"
]


def get_teams():
    team_dict = dict()
    final_dates = set()
    for team in TEAMS:
        sched = Schedule(team)
        games = []
        for game in sched:
            gamedate = dt.datetime.strptime(game.date, '%a, %b %d, %Y')
            games.append(gamedate)
            final_dates.update({gamedate})
        team_dict.update({team: np.array(games)})

    return {'dates': final_dates, 'teams': team_dict}


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


def build_conflict_metrics():
    data = get_teams()
    # 3.0 Calculating each team's score
    final_dates = np.array(list(data['dates']))
    team_dict = data['teams']
    # 3.1 Builds a date-vector for each team
    table_dict = {team: np.isin(final_dates, dates).astype(int) for team, dates in team_dict.items()}
    date_table = pd.DataFrame.from_dict(table_dict)
    create_schedule_vector(date_table)
    create_conflict_matrix(date_table)
    create_playoff_score(date_table)


if __name__ == '__main__':
    build_conflict_metrics()
