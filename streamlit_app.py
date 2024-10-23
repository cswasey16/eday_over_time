import streamlit as st
import pandas as pd
import datetime
import math
from pathlib import Path

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
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''



t = st.time_input("The current time is", value = datetime.time(8, 45))
st.write("Now showing the state at", t)


d = st.date_input("The current date is", datetime.date(2020, 11, 4))
st.write("Now showing the state on:", d)


dt = pd.to_datetime(d+t)
print (dt)

NC_df = NC_df.set_index('full_time')
nearest = NC_df.index.get_loc(dt, method='nearest')

st.write("The state is:", nearest)

# Filter the data
filtered_NC_df = NC_df[
    (NC_df['date'] <= d) &
    (NC_df['time'] <= t)
]

st.header('Eday Returns', divider='gray')

''

st.line_chart(
    filtered_NC_df,
    x='full_time',
    y='bidenj',
)

''
''


st.header(f'Vote status on {d}', divider='gray')

''

cols = st.columns(4)
