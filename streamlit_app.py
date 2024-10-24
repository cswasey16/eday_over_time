import streamlit as st
import pandas as pd
import datetime
import math
from pathlib import Path
import pytz
import plotly
from plotly import graph_objs as go

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='How Votes Came In In 2020',
    page_icon=':earth_americas:', 
    layout = "wide"
)


# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_json_data(state_ref):
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    state_file_name = "data/" + state_ref + "_2020.json"
    DATA_FILENAME = Path(__file__).parent/state_file_name
    state_df = pd.read_json(DATA_FILENAME)

    state_df = state_df.join(
        pd.json_normalize(state_df['vote_shares'])
    ).drop('vote_shares', axis=1)



    # Convert years from string to integers
    state_df['timestamp'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.tz_convert('US/Eastern')
    state_df['time'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.time
    state_df['date'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.date
    state_df['full_time'] = state_df['timestamp']
   

    # convert vote share into categoricals for ease
    state_df['biden_2way'] = state_df['bidenj']/(state_df['bidenj']+state_df['trumpd'])
    state_df['closeness'] = pd.cut(state_df['biden_2way'], bins=[0, .45, .49,  .51, .55, 1 ], labels=['Trump Lead', 'Narrow Trump Lead', 'Tie', 'Narrow Biden Lead', 'Biden Lead'])
    

    state_df = state_df.set_index('full_time')
    state_df.sort_index(inplace=True)
    state_df_update = state_df.reset_index().drop_duplicates(subset='full_time', keep='last').set_index('full_time')
 
    return state_df_update

@st.cache_data
def read_liveblog_data():
    PA_liveblog = pd.read_csv("data/PA_extract.csv")
    PA_liveblog['convert_date'] = pd.to_datetime(PA_liveblog['date'], unit = 'ms', errors = "coerce", utc = True).dt.tz_convert('US/Eastern')

    return PA_liveblog

def plot_raw_data():
    global fig
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dat['timestamp'], y=dat['bidenj'], name='Biden', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=dat['timestamp'], y=dat['trumpd'], name='Trump', mode='lines+markers', line=dict(color="#FF0000")))
    fig.layout.update(title_text="Ballot Flow", 
                xaxis=dict(
        autorange=False,
        range=["2020-11-3 01:00:00", "2020-11-10 21:23:22.6871"],
        rangeslider=dict(
            autorange=False,
            range=["2020-11-3 01:00:00", "2020-11-10 21:23:22.6871"]
        ),
        type="date"
    ))
    fig.add_vline(x=date_in[0], line_dash = "dash", line_color = "white")
    fig.add_annotation(x=date_in[0], y=(biden_hold[0] + .2),
            text="You Are Here",
            showarrow=True)
    st.plotly_chart(fig, use_container_width=True)




# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# 2020 Election Night Throwback Tool

Do you remember where we were at at this point on election night 2020? This tool does.

Using checkpoints of election night data from NYT, this graphs how votes came in during the 2020 election so you can remember what we actually knew at any point in time.
'''


# Add some spacing
''
''
st.write("Let's remember when it was..")

left, middle, right = st.columns(3, vertical_alignment="bottom")
option = left.selectbox(
  'Which state would you like to see?',
    ('AZ', 'GA', 'MI', 'NC', 'PA','WI'))
t = right.time_input("Time (ET)", value = datetime.time(8, 45))
d = middle.date_input("Date", datetime.date(2020, 11, 3))


state_df = get_json_data(state_ref = option)

st.write("Now showing the state at", d, t)

dt_orig = datetime.datetime.combine(d, t)
timezone = pytz.timezone('America/New_York')
dt = timezone.localize(dt_orig) 



iloc_idx = state_df.index.get_indexer([dt], method='backfill')  # returns absolute index into df e.g. array([5])
loc_idx = state_df.index[iloc_idx]                             # if you want named index
my_val = state_df.loc[loc_idx]   


PA_liveblog = read_liveblog_data()
PA_liveblog = PA_liveblog.set_index('convert_date')
PA_liveblog = PA_liveblog.loc[PA_liveblog.index.notnull()]
PA_liveblog.sort_index(inplace=True)
iloc_idx = PA_liveblog.index.get_indexer([dt], method='backfill')  # returns absolute index into df e.g. array([5])
loc_idx = PA_liveblog.index[iloc_idx]                             # if you want named index

liveblog_val = PA_liveblog.loc[loc_idx]  


date_in = my_val['timestamp']
votes_in = my_val['votes']
eevp_in = my_val['eevp']
biden_in = my_val['bidenj']
biden_hold = my_val['bidenj']
status = my_val['closeness'][0]
max_votes = state_df['votes'].max()
curr_percent = round(votes_in[0] / max_votes, 3)


dat = state_df
col1, col2 = st.columns([0.7, 0.3])
with col1:
    plot_raw_data()
with col2:
    st.write("The last update was given at", date_in[0], "and currently there is a", status)
    st.write(str(votes_in[0]), " votes are currently counted")
    st.write("This is", str(curr_percent), " percent out of the", str(max_votes), "votes that will eventually be counted in", option)
    st.write("What did the NYT have to say right now? According to ", liveblog_val['author'][0], ":", liveblog_val['text_update'][0])



''


