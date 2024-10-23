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
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
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




    # The data above has columns like:
    # vote_shares
    # votes
    # eevp
    # eevp_source
    # timestamp

    #


    # Convert years from string to integers
    state_df['time'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.time
    state_df['date'] = pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.date
    state_df['full_time']= pd.to_datetime(state_df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
   

    return state_df

state_df = get_json_data(state_ref = "NC")

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# How Votes Came In During 2020 Eday
DRAFT DRAFT JANKY JANKY

Using checkpoints of election night data from NYT, graph how votes came in during the 2020 election
Compare where it was to your current point in time
'''

# Add some spacing
''
''



t = st.time_input("The current time is", value = datetime.time(8, 45))
st.write("Now showing the state at", t)


d = st.date_input("The current date is", datetime.date(2020, 11, 4))
st.write("Now showing the state on:", d)


dt = datetime.datetime.combine(d, t)

timezone = pytz.timezone('UTC')
dt = timezone.localize(dt) 
print (dt)



state_df = state_df.set_index('full_time')
state_df.sort_index(inplace=True)

iloc_idx = state_df.index.get_indexer([dt], method='nearest')  # returns absolute index into df e.g. array([5])
loc_idx = state_df.index[iloc_idx]                             # if you want named index

my_val = state_df.loc[loc_idx]    

date_in = my_val['timestamp']
votes_in = my_val['votes']
eevp_in = str(my_val['eevp'])
biden_in = str(my_val['bidenj'])

st.write(my_val)

st.write(str(votes_in[0]), " votes are currently counted")

max_votes = state_df['votes'].max()
curr_percent = round(votes_in[0] / max_votes, 3)

st.write("This is", curr_percent, " out of the", max_votes, "votes that will eventually be counted")


# Filter the data
filtered_state_df = state_df[
    (state_df['date'] <= d) &
    (state_df['time'] <= t)
]


''
''
dat = state_df
def plot_raw_data():
    global fig
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dat['timestamp'], y=dat['bidenj'], name='Biden', mode='lines+markers'))
    fig.add_trace(go.Scatter(x=dat['timestamp'], y=dat['trumpd'], name='Trump', mode='lines+markers'))
    fig.layout.update(title_text="Ballot Flow", 
                xaxis=dict(
        autorange=False,
        range=["2020-11-3 18:36:37.3129", "2020-11-10 05:23:22.6871"],
        rangeslider=dict(
            autorange=False,
            range=["2020-11-3 18:36:37.3129", "2020-11-10 05:23:22.6871"]
        ),
        type="date"
    ))
    fig.add_vline(x=date_in[0], line_color = "white")
    st.plotly_chart(fig, use_container_width=True)
plot_raw_data()



''

cols = st.columns(4)
