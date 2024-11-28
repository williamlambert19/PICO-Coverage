import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
import hashlib


data = json.load(open('editorial-topics.json'))
broad_concepts = {}
for concept in data['results']:
    broad_concepts[concept['label']] = concept['linkSuffix']

print('done')

def generate_dataset():
    base_url ='https://data.cochrane.org/pico-search?facetSize=100&facets=sex,age,condition,interventionClassification,procedure,material,outcomeClassification,outcomeDomain&contentType=http%3A%2F%2Fdata.cochrane.org%2Fontologies%2Fcontent%2FReviewVersion&' 
    end_url = '&pageSize=5&pageNo=1'
    broad_concept_coverage = pd.DataFrame(columns = ['Concept', 'Coverage', 'Type'])
    headers = {'Accept': 'application/json'}
    for key in broad_concepts.keys():
        uri = broad_concepts[key].split('=')[-1]
        if broad_concepts[key][0] == 'p':
            mid_url = 'p=('
            for i in range(len(uri.split(','))):
                if i == 0:
                    mid_url = mid_url + uri.split(',')[i]
                else:
                    mid_url = mid_url + '%7C%7C' + uri.split(',')[i]
            mid_url = mid_url + ')'
            type = 'Population'
        elif broad_concepts[key][0] == 'i':
            mid_url = broad_concepts[key]
            type = 'Intervention'
        elif broad_concepts[key][0] == 'o':
            mid_url = broad_concepts[key]
            type = 'Outcome'
        url = base_url + mid_url + end_url
        resp = requests.get(url, headers=headers)
        print(resp)
        data = resp.json()
        coverage = data['search']['totalResults']
        broad_concept_coverage.loc[len(broad_concept_coverage)] = [key, coverage, type]
        population = broad_concept_coverage[broad_concept_coverage['Type'] == 'Population']
        intervention = broad_concept_coverage[broad_concept_coverage['Type'] == 'Intervention']
        outcome = broad_concept_coverage[broad_concept_coverage['Type'] == 'Outcome']
        all = broad_concept_coverage
        data = { 'all': all,
                 'population': population,
                 'intervention': intervention,
                 'outcome': outcome }
    return data

data = generate_dataset()
overall_data = data['all']
population_data = data['population']
intervention_data = data['intervention']
outcome_data = data['outcome']



st.title('PICO Coverage')

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overall", "Population", "Intervention", "Outcome", "Treemap"])
with tab1:
    fig = px.bar(
        overall_data,
        x='Concept',
        y='Coverage',
        color='Type', 
        hover_data=['Concept', 'Coverage'])
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    fig = px.bar(
        population_data,
        x='Concept',
        y='Coverage',
        color='Type', 
        hover_data=['Concept', 'Coverage'])
    st.plotly_chart(fig)

with tab3:
    fig = px.bar(
        intervention_data,
        x='Concept',
        y='Coverage',
        color='Type', 
        hover_data=['Concept', 'Coverage'])
    st.plotly_chart(fig)

with tab4:
    fig = px.bar(
        outcome_data,
        x='Concept',
        y='Coverage',
        color='Type', 
        hover_data=['Concept', 'Coverage'])
    st.plotly_chart(fig)

with tab5:
    fig = px.treemap(
        overall_data,
        path=['Concept'],
        values='Coverage',
        color='Concept',
        )
    
    fig.update_traces(customdata=overall_data[['Concept','Type']])

    fig.update_traces(hovertemplate=
                      'Coverage: %{value}<br>' +
                      'Concept: %{customdata[0]}<br>' 
                      'Type: %{customdata[1]}<br>'
                      )
    st.plotly_chart(fig, use_container_width=True)