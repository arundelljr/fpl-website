import streamlit as st
import requests
# import json
import datetime
import pandas as pd
from pprint import pprint
import numpy as np
import matplotlib.pyplot as plt

# wide layout
st.set_page_config(layout="wide")

#################
#    Caching    #
#################

# session-state version used to force cache invalidation on demand
if 'cache_version' not in st.session_state:
    st.session_state.cache_version = 0
if 'last_refreshed' not in st.session_state:
    st.session_state.last_refreshed = None

# Refresh Cache button - increments cache_version and reruns the app
if st.button("Refresh Cache"):
    # st.session_state.cache_version += 1
    # st.session_state.last_refreshed = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # st.rerun()
    pass

# reuse HTTP session across reruns
@st.cache_resource
def get_session():
    s = requests.Session()
    s.headers.update({"User-Agent": "fpl-app/1.0"})
    return s

# cached JSON fetcher with long TTL (7 days = 604800 seconds)
@st.cache_data(ttl=604800)
def fetch_json_cached(url: str, cache_version: int):
    session = get_session()
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()

f"""
Welcome to 12blokesandashedloadofFPL.
The last refresh occured at {st.session_state.last_refreshed}
"""

#################
# Fetching data #
#################

response = fetch_json_cached("https://fantasy.premierleague.com/api/leagues-classic/787217/standings/", st.session_state.cache_version)
league_info = response

player_team_ids = {player['player_name'] : player['entry'] for player in league_info['standings']['results']}

player_point_history = {}
for player, team_id in player_team_ids.items():
    response = fetch_json_cached(f"https://fantasy.premierleague.com/api/entry/{team_id}/history/", st.session_state.cache_version)
    gw_history = response
    points_history = {gw['event'] : gw['points'] for gw in gw_history['current']}
    player_point_history[f'{player}'] = points_history

    player_point_history_df = pd.DataFrame(player_point_history)

# form_df = pd.DataFrame(np.sum(player_point_history_df.iloc[-5:, :], axis=0), columns=['last_five_gameweeks']).sort_values(by='last_five_gameweeks', ascending=False)
# form_df.index = range(1, 13)
form_df = (
    player_point_history_df
    .iloc[-5:]
    .sum()
    .reset_index()
    .rename(columns={'index': 'player', 0: 'last_five_gameweeks'})
    .sort_values(by='last_five_gameweeks', ascending=False)
)
form_df.index = range(1, len(form_df) + 1)


league_table = {player['rank_sort'] : [player['player_name'], player['total']] for player in league_info['standings']['results']}

league_table_df = pd.DataFrame(league_table, index=['name', 'total']).T
league_table_df.index = range(1, len(league_table_df) + 1)


# Highest Gameweek Score
max_scores = player_point_history_df.max()
max_indices = player_point_history_df.idxmax()

max_scores_df = pd.DataFrame({
    'max_score': max_scores,
    'gameweek': max_indices
})
max_scores_df = max_scores_df.reset_index().rename(columns={"index": "player_name"})
max_scores_df.sort_values(by='max_score', ascending=False, inplace=True)
max_scores_df.index = range(1, len(max_scores_df) + 1)


# Highest Total left on the bench
gameweeks_so_far = len(player_point_history_df)
all_bench_history = {}
for player, team_id in player_team_ids.items():
    player_bench_history = {}
    for gameweek in range(1, gameweeks_so_far+1):
        response = fetch_json_cached(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{gameweek}/picks/", st.session_state.cache_version)
        gameweek_info = response
        bench_points = gameweek_info['entry_history']['points_on_bench']
        player_bench_history[gameweek] = bench_points
    all_bench_history[player] = player_bench_history

all_bench_history_df = pd.DataFrame(all_bench_history)
# all_bench_history_df = all_bench_history_df.reset_index().rename(columns={"index": "player_name"})
# all_bench_history_df.index = range(1, len(all_bench_history_df) + 1)


total_bench_scores = all_bench_history_df.sum().sort_values(ascending=False)

total_bench_scores_df = pd.DataFrame(total_bench_scores).rename(columns={0 : 'bench_score'})
total_bench_scores_df = total_bench_scores_df.reset_index().rename(columns={"index": "player_name"})
total_bench_scores_df.index = range(1, len(total_bench_scores_df) + 1)


# Highest Bench Scores
max_scores = all_bench_history_df.max()
max_indices = all_bench_history_df.idxmax()

max_bench_scores_df = pd.DataFrame({
    'max_bench_score': max_scores,
    'gameweek': max_indices
})

max_bench_scores_df = max_bench_scores_df.reset_index().rename(columns={"index": "player_name"})
max_bench_scores_df.sort_values(by='max_bench_score', ascending=False, inplace=True)
max_bench_scores_df.index = range(1, len(max_bench_scores_df) + 1)


# Projections based on form scores carried on for rest of season
gameweeks_left = 38 - gameweeks_so_far

form_proj_df = league_table_df.copy()
form_proj_df = form_proj_df.merge(form_df, left_on='name', right_on='player')
form_proj_df['form_points_per_GW'] = (form_proj_df['last_five_gameweeks']/5).astype(int)
form_proj_df['final_score_projection'] = form_proj_df.total + form_proj_df.form_points_per_GW*gameweeks_left
form_proj_df = form_proj_df[['name', 'final_score_projection']].sort_values(by='final_score_projection', ascending=False)
form_proj_df.index = range(1, len(form_proj_df) + 1)


# historic league table
# for every person take the total points from the gameweek history
running_total_history = {}
for player, team_id in player_team_ids.items():
    response = requests.get(f"https://fantasy.premierleague.com/api/entry/{team_id}/history/")
    gw_history = response.json()
    total_points = {gw['event'] : gw['total_points'] for gw in gw_history['current']}
    running_total_history[f'{player}'] = total_points

running_total_history_df = pd.DataFrame(running_total_history, columns=running_total_history.keys())
gameweek_player_rank_df = running_total_history_df.rank(axis=1, method='min', ascending=False).astype(int)


# Plotting
fig, ax = plt.subplots(figsize=(8, 5))
ax.invert_yaxis()

for user in gameweek_player_rank_df.columns:
    ranks = gameweek_player_rank_df[user].values
    ax.plot(gameweek_player_rank_df.index, ranks, marker='o', label=user)

    # Label the last point
    last_x = gameweek_player_rank_df.index[-1] + 0.65
    last_y = ranks[-1]
    ax.text(last_x, last_y, user, fontsize=10, va='center', ha='left')

# Set y-axis ticks
max_rank = gameweek_player_rank_df.values.max()
ax.set_yticks(range(1, max_rank + 1))

# Labels and title
ax.set_title('League Tracker')
ax.set_xlabel('Gameweek')
ax.set_ylabel('Rank')
ax.grid(True)
fig.tight_layout()


# Chip record
gameweeks_so_far = len(player_point_history_df)
league_chip_record = {}

for player, team_id in player_team_ids.items():
    player_chip_record = {}
    for n in range(1, gameweeks_so_far+1):
        response = fetch_json_cached(f"https://fantasy.premierleague.com/api/entry/{team_id}/event/{n}/picks/", st.session_state.cache_version)
        gameweek_info = response
        active_chip = gameweek_info['active_chip']
        if active_chip:
            chip_points = gameweek_info['entry_history']['points'] - gameweek_info['entry_history']['event_transfers_cost']
            player_chip_record[f'{active_chip}'] = chip_points

    league_chip_record[player] = player_chip_record

league_chip_record_df = pd.DataFrame(league_chip_record).T
league_chip_record_df['total_chip_score'] = league_chip_record_df.sum(axis=1)

league_chip_record_df = league_chip_record_df.sort_values(by='total_chip_score', ascending=False).reset_index().rename(columns={"index": "player_name"})
league_chip_record_df.index = range(1, len(league_chip_record_df) + 1)
