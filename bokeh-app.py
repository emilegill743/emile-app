# Import the necessary modules
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd

# Getting data
confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

confirmed_df = pd.read_csv(confirmed_url)

country_confirmed_df = confirmed_df.copy()
country_confirmed_df.drop(columns=['Province/State', 'Lat', 'Long'],
                     inplace=True)

country_confirmed_df = pd.melt(frame=country_confirmed_df,
                               id_vars=['Country/Region'],
                               var_name='Date',
                               value_name='Cases')

country_confirmed_df['Date'] = pd.to_datetime(country_confirmed_df['Date'],
                                              format='%m/%d/%y')

country_confirmed_df = country_confirmed_df.groupby(['Country/Region', 'Date']).sum().unstack(level=0)

# country_confirmed_df.drop(columns=('Cases','China'), inplace=True)

data = country_confirmed_df['Cases', 'United Kingdom']

# Make the ColumnDataSource: source
source = ColumnDataSource(data={
    'x'       : data.index,
    'y'       : data.values
})

# Create the figure: plot
plot = figure(title='Covid-19 UK', x_axis_type='datetime', plot_height=400, plot_width=700)

# Add circle glyphs to the plot
plot.circle(x='x', y='y', fill_alpha=0.8, source=source)

# Set the x-axis label
plot.xaxis.axis_label ='Date'

# Set the y-axis label
plot.yaxis.axis_label = 'Cases'

# Add the plot to the current document and add a title
curdoc().add_root(plot)
curdoc().title = 'Covid-19 UK'