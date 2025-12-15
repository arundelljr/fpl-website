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

st.markdown("""
            # Welcome to **12blokesandashedloadoffpl**
            """)


#################
#    Caching    #
#################

if 'cache_version' not in st.session_state:
    st.session_state.cache_version = 0
if 'last_refreshed' not in st.session_state:
    st.session_state.last_refreshed = None


if st.button("Refresh Cache"):
    # # update visible state
    # st.session_state.cache_version += 1
    # st.session_state.last_refreshed = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # # # clear cached data and resources on this process/instance
    # # st.cache_data.clear()        # clears functions decorated with @st.cache_data
    # # st.cache_resource.clear()    # clears functions decorated with @st.cache_resource

    # # force the app to rerun immediately with cleared caches
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
st.session_state['form_df'] = form_df

league_table = {player['rank_sort'] : [player['player_name'], player['total']] for player in league_info['standings']['results']}

league_table_df = pd.DataFrame(league_table, index=['name', 'total']).T
league_table_df.index = range(1, len(league_table_df) + 1)
st.session_state['league_table_df'] = league_table_df

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
st.session_state['max_scores_df'] = max_scores_df

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
st.session_state['total_bench_scores_df'] = total_bench_scores_df

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
st.session_state['max_bench_scores_df'] = max_bench_scores_df

# Projections based on form scores carried on for rest of season
gameweeks_left = 38 - gameweeks_so_far

form_proj_df = league_table_df.copy()
form_proj_df = form_proj_df.merge(form_df, left_on='name', right_on='player')
form_proj_df['form_points_per_GW'] = (form_proj_df['last_five_gameweeks']/5).astype(int)
form_proj_df['final_score_projection'] = form_proj_df.total + form_proj_df.form_points_per_GW*gameweeks_left
form_proj_df = form_proj_df[['name', 'final_score_projection']].sort_values(by='final_score_projection', ascending=False)
form_proj_df.index = range(1, len(form_proj_df) + 1)
st.session_state['form_proj_df'] = form_proj_df


# historic league table
# for every person take the total points from the gameweek history
running_total_history = {}
for player, team_id in player_team_ids.items():
    response = fetch_json_cached(f"https://fantasy.premierleague.com/api/entry/{team_id}/history/", st.session_state.cache_version)
    gw_history = response
    total_points = {gw['event'] : gw['total_points'] for gw in gw_history['current']}
    running_total_history[f'{player}'] = total_points

running_total_history_df = pd.DataFrame(running_total_history, columns=running_total_history.keys())
running_rank_df = running_total_history_df.rank(axis=1, method='min', ascending=False).astype(int)
st.session_state['running_rank_df'] = running_rank_df

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

# score per chip used
# if "columns 2,3,4,5" means 1-based positions, use iloc[:, 1:5]
cols_slice = league_chip_record_df.iloc[:, 0:4]
# If some cells contain the string 'None' or empty strings, normalise them to NaN first:
cols_slice = cols_slice.replace({'None': np.nan})
# count non-None / non-NaN per row
count_non_none = cols_slice.notna().sum(axis=1)
# compute score per chip, avoid division by zero by using NaN for zero counts
league_chip_record_df['score_per_chip'] = round(
    league_chip_record_df['total_chip_score'] / count_non_none.replace(0, np.nan), 1
)

league_chip_record_df = league_chip_record_df.sort_values(by='score_per_chip', ascending=False).reset_index().rename(columns={"index": "player_name"})
league_chip_record_df.index = range(1, len(league_chip_record_df) + 1)
st.session_state['league_chip_record_df'] = league_chip_record_df


# Top score per gameweek
# For each gameweek (row) find the highest score and the player who scored it
top_scores_per_gw = player_point_history_df.max(axis=1)
top_players_per_gw = player_point_history_df.idxmax(axis=1)

top_scores_per_gw_df = pd.DataFrame({
    'gameweek': top_scores_per_gw.index,
    'player_name': top_players_per_gw.values,
    'score': top_scores_per_gw.values
})

# Normalise index to 1-based sequential integers like other tables
top_scores_per_gw_df = top_scores_per_gw_df.reset_index(drop=True)
top_scores_per_gw_df.index = range(1, len(top_scores_per_gw_df) + 1)

st.session_state['top_scores_per_gw_df'] = top_scores_per_gw_df
