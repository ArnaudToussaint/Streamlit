import streamlit as st
import pandas as pd
import numpy as np

import requests
import json

def find(element, JSON, path, all_paths):    
  if element in JSON:
    path = path + element + ' = ' + JSON[element].encode('utf-8')
    st.write(path)
    all_paths.append(path)
  for key in JSON:
    if isinstance(JSON[key], dict):
      find(element, JSON[key],path + key + '.',all_paths)

st.set_page_config(page_title="Test MAP", layout='wide')

data_url='https://geo.api.gouv.fr/communes?codePostal=78260&fields=nom,code,codesPostaux,centre,surface,contour,bbox,codeDepartement,departement,codeRegion,region,population,zone&format=json&geometry=centre'
response = requests.get(data_url).json()

df = pd.DataFrame(response)

st.dataframe(
  data=df, 
  #width=None, 
  #height=None, 
  #*, 
  use_container_width=True, 
  hide_index=True, 
  column_order=None, 
  column_config=None,  
  key=None, 
  on_select="ignore", 
  selection_mode="multi-row")

#st.write(response)
        
try:
  df_contour=df["contour"]
  st.write(df_contour['type'])
  st.dataframe(df_contour)

  all_paths = []
  find("coordinates",response,'',all_paths)
  
except:
  st.write("TRY2: An exception occurred")
  
#df = pd.DataFrame({
#    "col1": np.random.randn(1000) / 50 + 37.76,
#    "col2": np.random.randn(1000) / 50 + -122.4,
#    "col3": np.random.randn(1000) * 100,
#    "col4": np.random.rand(1000, 4).tolist(),
#})

#st.map(df_contour,
#    latitude='col1',
#    longitude='col2'
#    )
