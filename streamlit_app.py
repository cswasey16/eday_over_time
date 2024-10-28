import streamlit as st
import pandas as pd
import datetime
import math
from pathlib import Path
import pytz
import plotly
from plotly import graph_objs as go
import markdown
from bs4 import BeautifulSoup


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='How Votes Came In In 2020',
    page_icon=':earth_americas:', 
    layout = "wide"
)


# -----------------------------------------------------------------------------
# Declare some useful functions.
def strip_markdown(text):
    html = markdown.markdown(text)
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


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
    # convert vote share into categoricals for ease
    state_df['biden_2way'] = state_df['bidenj']/(state_df['bidenj']+state_df['trumpd'])
    state_df['closeness'] = pd.cut(state_df['biden_2way'], bins=[0, .45, .49,  .51, .55, 1 ], labels=['Trump Lead', 'Narrow Trump Lead', 'Tie', 'Narrow Biden Lead', 'Biden Lead'])



    # Convert years from string to integers
    state_df['timestamp'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.tz_convert('US/Eastern')
    state_df['time'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.time
    state_df['date'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.date
    state_df['full_time'] = state_df['timestamp']


   
    min_row = state_df[state_df['votes']==state_df['votes'].min()]
    min_row['timestamp'] = pd.to_datetime('2020-11-03 00:06:36', format='%Y-%m-%d %H:%M:%S').tz_localize('US/Eastern')
    min_row['time'] = pd.to_datetime(min_row['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.time
    min_row['date'] = pd.to_datetime(min_row['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.date
    min_row['full_time'] = min_row['timestamp']
    min_row['votes'] = 0 
    min_row['biden_2way'] = 0.5
    min_row['bidenj'] = 0.5
    min_row['trumpd'] = 0.5
    min_row['closeness'] = 'No Data'

    min_row_2 = min_row
    min_row_2['timestamp'] = pd.to_datetime('2020-11-03 00:08:36', format='%Y-%m-%d %H:%M:%S').tz_localize('US/Eastern')
    min_row_2['time'] = pd.to_datetime(min_row_2['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.time
    min_row_2['date'] = pd.to_datetime(min_row_2['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.date
    min_row_2['full_time'] = min_row_2['timestamp']

    state_df = pd.concat([state_df, min_row], ignore_index=True)
    state_df = pd.concat([state_df, min_row_2], ignore_index=True)
##ADD BEFORE-EVERYTHING DATA POINT WITH "NO DATA"
    state_df = state_df.set_index('full_time')
    state_df.sort_index(inplace=True)
    state_df_update = state_df.reset_index().drop_duplicates(subset='full_time', keep='last').set_index('full_time')

    return state_df_update

@st.cache_data
def read_liveblog_data():
    PA_liveblog = pd.read_csv("data/PA_extract.csv")
    PA_liveblog['convert_date'] = pd.to_datetime(PA_liveblog['date'], unit = 'ms', errors = "coerce", utc = True).dt.tz_convert('US/Eastern')

    PA_liveblog['text_update'] = PA_liveblog['text_update'].apply(strip_markdown)

    return PA_liveblog

def filter_to_current(data, timestamp ):
    timezone = pytz.timezone('America/New_York')
    dt = timezone.localize(pd.to_datetime("2020-11-2 01:00:00"))

    new_df = data.loc[dt:timestamp]

    return new_df

def plot_raw_data(dat):
    global fig
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dat['timestamp'], y=dat['bidenj'], name='Biden', mode='lines'))
    fig.add_trace(go.Scatter(x=dat['timestamp'], y=dat['trumpd'], name='Trump', mode='lines', line=dict(color="#FF0000")))
    fig.layout.update(title_text="Ballot Flow", 
                xaxis=dict(
        autorange=False,
        range=["2020-11-3 05:00:00", "2020-11-5 21:23:22.6871"],
        type="date"
    ))
    fig.add_vline(x=date_in, line_dash = "dash", line_color = "white")
    ### Add markings for polls close ET/PST/etc?
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



 

left, right = st.columns([0.3, 0.7], vertical_alignment="top")
option = left.selectbox(
  'Select State',
    ('AZ', 'GA', 'MI', 'NC', 'PA','WI'))

start_date = datetime.datetime(2020, 11, 3) + datetime.timedelta(hours=6)
end_date = start_date + datetime.timedelta(days=2)
current_time = pd.Timestamp.now()
current_hour = current_time.to_pydatetime().hour
current_time = start_date + pd.to_timedelta(current_hour, unit='h')


left2, right2 = st.columns([0.7, 0.3], vertical_alignment="top")
t = left2.slider(
    "Remember when it was...",
    min_value=start_date,
    max_value=end_date,
    value=current_time,
    format="MMMM DD hhA",
    step=datetime.timedelta(hours=1),
)


state_df = get_json_data(state_ref = option)



dt_orig = t
timezone = pytz.timezone('America/New_York')
dt = timezone.localize(dt_orig) 

state_curr = filter_to_current(data = state_df, timestamp= dt)


iloc_idx = state_df.index.get_indexer([dt], method='ffill')  # returns absolute index into df e.g. array([5])
loc_idx = state_df.index[iloc_idx]                             # if you want named index
my_val = state_df.loc[loc_idx]



PA_liveblog = read_liveblog_data()
PA_liveblog = PA_liveblog.set_index('convert_date')
PA_liveblog = PA_liveblog.loc[PA_liveblog.index.notnull()]
PA_liveblog.sort_index(inplace=True)
iloc_idx = PA_liveblog.index.get_indexer([dt], method='backfill')  # returns absolute index into df e.g. array([5])
loc_idx = PA_liveblog.index[iloc_idx]                             # if you want named index

liveblog_val = PA_liveblog.loc[loc_idx]  


date_in = my_val['timestamp'].iloc[0]
votes_in = my_val['votes']
eevp_in = my_val['eevp']
biden_in = my_val['bidenj']
biden_hold = my_val['bidenj']
status = my_val['closeness'].iloc[0]
max_votes = state_df['votes'].max()
curr_percent = round(votes_in.iloc[0] / max_votes, 3)


col1, col2 = st.columns([0.7, 0.3])
with col1:
    plot_raw_data(state_curr)
with col2:
    st.write("The last update was given at", date_in.strftime("%I:%M%p"), "and currently there is a", status)
    st.write(str(votes_in.iloc[0]), " votes are currently counted")
    st.write("This is", str(curr_percent), " percent out of the", str(max_votes), "votes that will eventually be counted in", option)
    st.write("What did the NYT have to say right now? According to ", liveblog_val['author'].iloc[0], ":", liveblog_val['text_update'].iloc[0])



''


