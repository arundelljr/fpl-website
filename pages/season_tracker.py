import streamlit as st
# import requests
# import json
# import pandas as pd
# from pprint import pprint
# import numpy as np
import matplotlib.pyplot as plt

# from get_data import running_rank_df

running_rank_df = st.session_state.get('running_rank_df')

# Plotting
fig, ax = plt.subplots(figsize=(8, 5))
ax.invert_yaxis()

for user in running_rank_df.columns:
    ranks = running_rank_df[user].values
    ax.plot(running_rank_df.index, ranks, marker='o', label=user)

    # Label the last point
    last_x = running_rank_df.index[-1] + 0.85
    last_y = ranks[-1]
    ax.text(last_x, last_y, user, fontsize=10, va='center', ha='left')

# Set y-axis ticks
max_rank = running_rank_df.values.max()
ax.set_yticks(range(1, max_rank + 1))

# Labels and title
ax.set_title('League Tracker')
ax.set_xlabel('Gameweek')
ax.set_ylabel('Rank')
ax.grid(True)
fig.tight_layout()

st.pyplot(fig, width=1000)
