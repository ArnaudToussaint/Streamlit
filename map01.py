import streamlit as st
import pandas as pd
import numpy as np

import requests
import json

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

try:
  st.write(response)
  st.write(response['contour'])
except:
  st.write("TRY1: An exception occurred")
        
try:
  st.dataframe(df)
  df_contour=df.loc["contour"]
  st.dataframe(df_contour)
except:
  st.write("TRY2: An exception occurred")
  
#df = pd.DataFrame({
#    "col1": np.random.randn(1000) / 50 + 37.76,
#    "col2": np.random.randn(1000) / 50 + -122.4,
#    "col3": np.random.randn(1000) * 100,
#    "col4": np.random.rand(1000, 4).tolist(),
#})

#st.map(df,
#    latitude='col1',
#    longitude='col2'
#    )
