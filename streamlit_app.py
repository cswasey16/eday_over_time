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
def get_json_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/NC_2020.json'
    NC_df = pd.read_json(DATA_FILENAME)

    NC_df = NC_df.join(
        pd.json_normalize(NC_df['vote_shares'])
    ).drop('vote_shares', axis=1)




    # The data above has columns like:
    # vote_shares
    # votes
    # eevp
    # eevp_source
    # timestamp

    #


    # Convert years from string to integers
    NC_df['time'] = pd.to_datetime(NC_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.time
    NC_df['date'] = pd.to_datetime(NC_df['timestamp'], format='%Y-%m-%dT%H:%M:%S').dt.date
    NC_df['full_time']= pd.to_datetime(NC_df['timestamp'], format='%Y-%m-%dT%H:%M:%S')
   

    return NC_df

NC_df = get_json_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: How Votes Came In 2020
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

timezone = pytz.timezone('America/New_York')
dt = timezone.localize(dt) 
print (dt)



NC_df = NC_df.set_index('full_time')
NC_df.sort_index(inplace=True)

iloc_idx = NC_df.index.get_indexer([dt], method='nearest')  # returns absolute index into df e.g. array([5])
loc_idx = NC_df.index[iloc_idx]                             # if you want named index

my_val = NC_df.iloc[iloc_idx]
my_val = NC_df.loc[loc_idx]    

st.write("The state is:", my_val)

# Filter the data
filtered_NC_df = NC_df[
    (NC_df['date'] <= d) &
    (NC_df['time'] <= t)
]


''
''
dat = NC_df
def plot_raw_data():
    global fig
    fig = go.Figure()
    fig.add_trace(go.Line(x=dat['timestamp'], y=dat['bidenj'], name='Biden'))
    fig.add_trace(go.Line(x=dat['timestamp'], y=dat['trumpd'], name='Trump'))
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
    st.plotly_chart(fig, use_container_width=True)
plot_raw_data()



''

cols = st.columns(4)
