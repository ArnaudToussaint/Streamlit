import streamlit as st
import pandas as pd
import numpy as np

import requests
import json

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
    #"""Returns molecular image as data URI."""
    base_url = 'https://api.gouv.fr'
    real_url = base_url+img
    return real_url

#st.write("Start FOR")
#for element in response: 
#  for value in response[7]:  #response['Name_OF_YOUR_KEY/ELEMENT']:
#    st.write(response[7])   #print(response['Name_OF_YOUR_KEY/ELEMENT']['INDEX_OF_VALUE']['VALUE'])
#st.write("End FOR")

df = pd.DataFrame(response)
df["logo"] = df["logo"].apply(smi_to_png)
df["path"] = df["path"].apply(smi_to_png)

col1, col2 = st.columns(2)

with col1:
    st.header("Original JSON")
    st.dataframe(
      data=response, 
      #width=None, 
      #height=None, 
      #*, 
      use_container_width=True, 
      hide_index=None, 
      column_order=None, 
      #column_config=None, 
      column_config=None,  
      key=None, 
      on_select="ignore", 
      selection_mode="multi-row")
with col2:
    st.header("Updated JSON")
    st.dataframe(
      data=df, 
      #width=None, 
      #height=None, 
      #*, 
      use_container_width=True, 
      hide_index=True, 
      column_order={"logo","owner","title","openness","tagline","Définition","URL","owner_acronym","datagouv_uuid","slug"}, 
      #column_config=None, 
      column_config={
          "path": st.column_config.LinkColumn( "Définition", help="Official link" ),
          "logo": st.column_config.ImageColumn( "Logo", help="API's logo" ),
          "datapass_link": st.column_config.LinkColumn( "URL", help="Official link" )
      },  
      key=None, 
      on_select="ignore", 
      selection_mode="multi-row")
