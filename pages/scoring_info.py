import streamlit as st
import pandas as pd

max_scores_df = st.session_state.get('max_scores_df')
league_chip_record_df = st.session_state.get('league_chip_record_df')
total_bench_scores_df = st.session_state.get('total_bench_scores_df')
max_bench_scores_df = st.session_state.get('max_bench_scores_df')
top_scores_per_gw_df = st.session_state.get('top_scores_per_gw_df')

st.markdown('## Scoring Insights')

# Row of three small tables
cols = st.columns(3)

with cols[0]:
    st.subheader('Top Single GW Scores')
    if max_scores_df is not None:
        st.dataframe(max_scores_df.head(6).reset_index(drop=True), height=220)
    else:
        st.info('Max scores not available')

with cols[1]:
    st.subheader('Total Bench Penalty')
    if total_bench_scores_df is not None:
        # show a bar chart of bench scores
        bench_chart = total_bench_scores_df.set_index('player_name')['bench_score']
        st.bar_chart(bench_chart)
    else:
        st.info('Bench totals not available')

with cols[2]:
    st.subheader('Highest Bench Instances')
    if max_bench_scores_df is not None:
        st.dataframe(max_bench_scores_df.head(6).reset_index(drop=True), height=220)
    else:
        st.info('Max bench scores not available')

st.markdown('---')

# Big row: chips + top scores per GW
col_chip, col_top = st.columns([1.6, 1])

with col_chip:
    st.subheader('Total Chip Scores')
    if league_chip_record_df is not None:
        # show top performers and a horizontal bar chart
        top_chips = league_chip_record_df.sort_values('total_chip_score', ascending=False).head(8)
        st.dataframe(top_chips[['player_name', 'total_chip_score', 'score_per_chip']].reset_index(drop=True), height=320)
        st.bar_chart(top_chips.set_index('player_name')['total_chip_score'])
    else:
        st.info('Chip data not available')

with col_top:
    st.subheader('Top Scores per Gameweek')
    if top_scores_per_gw_df is not None:
        # ensure gameweek is numeric index for plotting
        df = top_scores_per_gw_df.copy()
        try:
            df['gameweek'] = pd.to_numeric(df['gameweek'])
        except Exception:
            pass
        df_plot = df.set_index('gameweek')['top_score']
        st.line_chart(df_plot)
        st.dataframe(df.reset_index(drop=True), height=200)
    else:
        st.info('Top scores per GW not available yet')
