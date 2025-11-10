import streamlit as st
# import requests
# import json
# import pandas as pd
# from pprint import pprint
# import numpy as np
import matplotlib.pyplot as plt

from get_data import gameweek_player_rank_df

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

st.pyplot(fig, width=1000)
