import streamlit as st
# import requests
# import json
# import pandas as pd
# from pprint import pprint
# import numpy as np
# import matplotlib.pyplot as plt

# from get_data import max_scores_df, league_chip_record_df, total_bench_scores_df, max_bench_scores_df

max_scores_df = st.session_state.get('max_scores_df')
league_chip_record_df = st.session_state.get('league_chip_record_df')
total_bench_scores_df = st.session_state.get('total_bench_scores_df')
max_bench_scores_df = st.session_state.get('max_bench_scores_df')
top_scores_per_gw_df = st.session_state.get('top_scores_per_gw_df')

col1, col2, col3 = st.columns([1, 1, 1.2])

with col1:
    # st.write("League Table")
    # st.dataframe(league_table_df, height=460)

    st.write("Highest Scores")
    st.dataframe(max_scores_df, height=460)



with col2:
    # st.write("Form Table (last 5 GWs)")
    # st.dataframe(form_df, height=460)

    st.write("Total Points left on the Bench")
    st.dataframe(total_bench_scores_df, height=460)


with col3:
    # st.write("Final Projection if last 5 GW form is continued")
    # st.dataframe(form_proj_df, height=460)

    st.write("Highest Points left on the Bench")
    st.dataframe(max_bench_scores_df, height=460)


# st.write("Bench History")
# st.dataframe(all_bench_history_df)

col_chip, col_top = st.columns([2, 1])

with col_chip:
    st.write("Total Chip Scores")
    st.dataframe(league_chip_record_df, height=460)

with col_top:
    st.write("Top Scores per Gameweek")
    st.dataframe(top_scores_per_gw_df, height=460, hide_index=True)
