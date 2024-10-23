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


    # The data above has columns like:
    # vote_shares
    # votes
    # eevp
    # eevp_source
    # timestamp

    #


    # Convert years from string to integers
    NC_df['Time'] = pd.to_datetime(NC_df['timestamp'], format='%Y-%m-%dT%H:%M:%S')

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

min_value = NC_df['Time'].min()
max_value = NC_df['Time'].max()


yearmin = NC_df['Time'].min().year
monthmin = NC_df['Time'].min().month
daymin = NC_df['Time'].min().day

yearmax = NC_df['Time'].max().year
monthmax = NC_df['Time'].max().month
daymax = NC_df['Time'].max().day


PRE_SELECTED_DATES = (datetime.datetime(yearmin,monthmin,daymin), datetime.datetime(yearmax,monthmax,daymax ))
min = datetime.datetime(yearmin,monthmin,daymin)
max = datetime.datetime(yearmax,monthmax,daymax)

from_year, to_year = st.slider(
    'Which times are you interested in?',
    min_value=min,
    max_value=max,
    value=PRE_SELECTED_DATES)

''
''
''

# Filter the data
filtered_NC_df = NC_df[
    (NC_df['Time'] <= to_year)
    & (from_year <= NC_df['Time'])
]

st.header('Eday Returns', divider='gray')

''

st.line_chart(
    filtered_NC_df,
    x='Time',
    y='Votes',
)

''
''


first_year = NC_df[NC_df['Time'] == from_year]
last_year = NC_df[NC_df['Time'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)
