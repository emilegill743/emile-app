# Import the necessary modules
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, CheckboxGroup
from bokeh.plotting import figure, show
from bokeh.palettes import Spectral11
from bokeh.layouts import widgetbox, row
import pandas as pd
import numpy as np
import itertools

# Get Johns Hopkins data from GitHub

confirmed_global_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
confirmed_global_df = pd.read_csv(confirmed_global_url)

# Preparing data for no. cases

cases_df = confirmed_global_df.copy()

cases_df.drop(columns=['Province/State', 'Lat', 'Long'], inplace=True)

cases_df = pd.melt(frame=cases_df,
             id_vars=['Country/Region'],
             var_name='Date',
             value_name='Cases')

cases_df['Date'] = pd.to_datetime(cases_df['Date'],
                            format='%m/%d/%y')

cases_df = cases_df.groupby(
                    ['Country/Region', 'Date']).sum()

cases_df = cases_df.unstack(level=0)['Cases']

# Comparing trajectories of countries

min_cases = 50 # case threshold to be considered infected
data = {}

for country in cases_df:
    
    country_df = cases_df[country][cases_df[country] > min_cases]
    country_df.index = range(len(country_df))
    
    if len(country_df) > 0:
        data[country_df.name] = country_df.apply(
                                    lambda x : np.log(x) if x > 0 else 0)
    
trajectories_df = pd.DataFrame(data)

# Creating trajectories plot

xs = [trajectories_df.index.values] * len(trajectories_df.columns)

ys = [trajectories_df[name].values for name in trajectories_df]

countries = [name for name in trajectories_df]

colors = [Spectral11[i%11] for i in range(len(trajectories_df.columns))]

source = ColumnDataSource(data={
                'xs' : xs,
                'ys' : ys,
                'country' : countries,
                'color' : colors})

plot = figure(title='Country Trajectories',
              width=800,
              height=600)

# Adding hover tool
hover = HoverTool(tooltips=[('Country', '@country')])
plot.add_tools(hover)

# Adding multi_line glyph of trajectories
plot.multi_line(xs='xs',
                ys='ys',
                source=source,
                line_color='color',
                line_width=2)

plot.xaxis.axis_label = 'Days since arrival'
plot.yaxis.axis_label = 'Cases'

def update_plot(attr, old, new):

    selected_countries = [checkbox_group.labels[i]
                          for i in checkbox_group.active]

    filtered_df = trajectories_df[selected_countries]

    xs_new = [filtered_df.index.values] * len(filtered_df.columns)

    ys_new = [filtered_df[name].values for name in filtered_df]

    countries_new = [name for name in filtered_df]

    colors_new = [Spectral11[i%11] for i in range(len(filtered_df.columns))]

    new_data = data={
                'xs' : xs_new,
                'ys' : ys_new,
                'country' : countries_new,
                'color' : colors_new}
    
    source.data = new_data


checkbox_group = CheckboxGroup(
                    labels=countries)

checkbox_group.on_change('active', update_plot)


# x = np.arange(len(trajectories_df))
# double_2days = [[*(x * np.log(2)) / 2] for i in x]
# double_3days = [[*(x * np.log(2)) / 3] for i in x]
# double_4days = [[*(x * np.log(2)) / 4] for i in x]

# plot.multi_line(xs = [[*x] for i in range(3)],
#                 ys =[double_2days, double_3days, double_4days],
#                 color='red')

# Add the plot to the current document and add a title
layout = row(widgetbox(checkbox_group), plot)
curdoc().add_root(layout)
curdoc().title = 'Covid-19 Trajectories'