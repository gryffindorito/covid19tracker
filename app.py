from pandas.io.parquet import FastParquetImpl
import streamlit as st
import pandas as pd
import numpy as np
import requests
from plotly.offline import iplot
import plotly.graph_objs as go
import plotly.express as px
from pandas.io.json import json_normalize
from streamlit.script_runner import StopException, RerunException

fig = go.Figure()

st.write("""
# COVID-19 Tracker

Source : [Corona Virus API](https://documenter.getpostman.com/view/10808728/SzS8rjbc?version=latest#81447902-b68a-4e79-9df9-1b371905e9fa)
""")

expand_bar = st.beta_expander("About")
expand_bar.markdown("""
This app tracks the spread of COVID-19 in various countries.
Users can :
* Choose the type of case (Active, Recovered, Deceased)
* Choose various countries and compare the impact of the pandemic in the same.
""")

url = 'https://api.covid19api.com/countries'
r = requests.get(url)
df0 = json_normalize(r.json())

index_us = df0.index[df0['Slug'] == 'united-states']
df0 = df0.drop(index_us)

top_row = pd.DataFrame({'Country':['Select a Country'], 'Slug': ['Empty'], 'ISO2': ['E']})
df0 = pd.concat([top_row, df0]).reset_index(drop = True)

st.sidebar.header('Search Filters')
graph_type = st.sidebar.selectbox('Cases Type', ('confirmed', 'deaths', 'recovered'))
st.sidebar.subheader('Search by Country')
country = st.sidebar.selectbox('Country', df0.Country)
country_compare = st.sidebar.selectbox('Select Another Country', df0.Country)

if country != 'Select a Country':
    slug = df0.Slug[df0['Country'] == country].to_string(index = False)[1:]
    url = 'https://api.covid19api.com/total/dayone/country/'+slug+'/status/'+graph_type
    r = requests.get(url)
    st.write("""## Total """+graph_type+""" cases in """+country+""" are : """ + str(r.json()[-1].get("Cases")))
    df = json_normalize(r.json())
    layout = go.Layout(
        title = country + '\'s ' + graph_type + ' cases Data.',
        xaxis = dict(title = 'Date'),
        yaxis = dict(title = 'No. of Cases'),)
    fig.update_layout(dict1 = layout, overwrite = True)
    fig.add_trace(go.Scatter(x = df.Date, y = df.Cases, mode = 'lines', name = country))

    if country_compare != "Select a Country":
        slug1 = df0.Slug[df0['Country']==country_compare].to_string(index=False)[1:]
        url = 'https://api.covid19api.com/total/dayone/country/'+slug1+'/status/'+graph_type
        r = requests.get(url)
        st.write("""## Total """+graph_type+""" cases in """+country_compare+""" are: """+str(r.json()[-1].get("Cases")))
        df = json_normalize(r.json())
        layout = go.Layout(
            title = country+' vs '+country_compare+' '+graph_type+' cases Data.',
            xaxis = dict(title = 'Date'),
            yaxis = dict(title = 'Number of cases'))
        
        fig.update_layout(dict1 = layout, overwrite = True)
        fig.add_trace(go.Scatter(x=df.Date, y=df.Cases, mode='lines', name=country_compare))
    
    st.plotly_chart(fig, use_container_width = True)

else:
    url = 'https://api.covid19api.com/world/total'
    r = requests.get(url)
    total = r.json()["TotalConfirmed"]
    deaths = r.json()["TotalDeaths"]
    recovered = r.json()["TotalRecovered"]

    st.write("""## Global Data""")
    st.write("Total cases: "+str(total)+", Total deaths: "+str(deaths)+", Total recovered: "+str(recovered))
    x = ["TotalCases", "TotalDeaths", "TotalRecovered"]
    y = [total, deaths, recovered]

    layout = go.Layout(
        title = 'Global Data',
        xaxis = dict(title = 'Category'),
        yaxis = dict(title = 'No. of Cases')
    )

    fig.update_layout(dict1 = layout, overwrite = True)
    fig.add_trace(go.Bar(name = 'Global Data', x = x, y = y))
    st.plotly_chart(fig, use_container_width= True)
