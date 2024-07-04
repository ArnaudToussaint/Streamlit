import streamlit as st
import pandas as pd
import numpy as np

import requests
import json

from streamlit import session_state as ss

st.set_page_config(page_title="Test", layout='wide')

#df = pd.DataFrame(np.random.randn(10, 20), columns=("col %d" % i for i in range(20)))
#st.dataframe(df.style.highlight_max(axis=0))

url1 = 'https://raw.githubusercontent.com/insightbuilder/python_de_learners_data/main/code_script_notebooks/python_scripts/json_reader/toplevel_comment_zGAkhN1YZXM.json'
url2 = 'https://www.hatvp.fr/agora/opendata/agora_repertoire_opendata.json'
url3 = 'https://api.gouv.fr/api/v1/apis'

response = requests.get(url3).json()
#st.dataframe(response)

#Base URL:             https://api.gouv.fr
# + JSON value / img:  /images/api-logo/mtes.png
@st.cache_data
def smi_to_png(img: str) -> str:
    base_url = 'https://api.gouv.fr'
    real_url = base_url+img
    return real_url

def smi_to_status(term: str) -> str:
    match term:
        case "closed":
             ret_val="🔴"
        case "semi_open":
             ret_val="🟠"
        case "open":
             ret_val="🟢"
        case _:
            ret_val=term
    return ret_val

#st.write("Start FOR")
#for element in response: 
#  for value in response[7]:  #response['Name_OF_YOUR_KEY/ELEMENT']:
#    st.write(response[7])   #print(response['Name_OF_YOUR_KEY/ELEMENT']['INDEX_OF_VALUE']['VALUE'])
#st.write("End FOR")

df = pd.DataFrame(response)
df["logo"] = df["logo"].apply(smi_to_png)
df["path"] = df["path"].apply(smi_to_png)
df["openness"] = df["openness"].apply(smi_to_status)

#col1, col2 = st.columns(2)
#with col1:                       
#    st.header("Original JSON")   
#    st.dataframe(                
#      data=response,             
#      #width=None,               
#      #height=None,              
#      #*,                        
#      use_container_width=True,  
#      hide_index=None,           
#      column_order=None,         
#      #column_config=None,       
#      column_config=None,        
#      key=None,                  
#      on_select="ignore",        
#      selection_mode="multi-row")
#with col2:
st.header("API officielles Gouv.fr")
df = df.sort_values(by="owner", ascending=True)

if "filters_options" not in ss:
    df = pd.DataFrame(response)
    df = df.sort_values(by="owner", ascending=True)
    ss.filters_options = ""

def apply_filters():
    st.write('Apply filters:'+ss.owners)
    ss.filters_options = ss.owners
    if ss.filters_options:
        ss.df = ss.df[ss.df.loc[['owner'] == ss.owners]]

owners = df['owner'].drop_duplicates()
owner_choice = st.sidebar.selectbox('Selection propriétaire:', owners, on_change=apply_filters, key='owners')

def make_filter_title():
    titles = df['owner'].loc[df['title'] == owner_choice]
    title_choice = st.sidebar.selectbox('Selection API', titles, key='titles')




st.dataframe(
  data=df, 
  #width=None, 
  height=None, 
  #*, 
  use_container_width=True, 
  hide_index=True, 
  column_order=("logo","owner","title","openness","tagline","path","datapass_link","slug","owner_acronym","datagouv_uuid"), 
  column_config={
      "title": st.column_config.TextColumn("API"),
      "owner": st.column_config.TextColumn("Propriétaire"),
      "openness": st.column_config.TextColumn("Statut"),
      "tagline": st.column_config.TextColumn("Définition"),
      "path": st.column_config.LinkColumn("Détail", help="Official Details link"),
      "logo": st.column_config.ImageColumn("Logo", help="Owner's logo"),
      "datapass_link": st.column_config.LinkColumn("URL", help="Official link")
  },  
  key=None, 
  on_select="ignore", 
  selection_mode="multi-row")
