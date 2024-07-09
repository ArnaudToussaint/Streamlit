import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from streamlit import session_state as ss
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

import requests
import json
import io

st.set_page_config(page_title="Test", layout='wide')
st.title("API officielles Gouv.fr")

key_values = {
    "title": "API",
    "owner": "Propriétaire",
    "openness": "Statut",
    "tagline":"Définition",
    "path":"Détail",
    "logo":"Logo",
    "datapass_link":"URL",
    "owner_acronym":"ID Propriétaire",
    "datagouv_uuid":"UUID",
    "slug":"API Tag"
}

@st.cache_data
def get_df_info(df):
    buffer = io.StringIO ()
    df.info (buf=buffer)
    lines = buffer.getvalue ().split ('\n')
    # lines to print directly
    lines_to_print = [0, 1, 2, -2, -3]
    for i in lines_to_print:
        st.write (lines [i])
    # lines to arrange in a df
    list_of_list = []
    for x in lines [5:-3]:
        list = x.split ()
        list_of_list.append (list)
    info_df = pd.DataFrame (list_of_list, columns=['index', 'Column', 'Non-null-Count', 'null', 'Dtype'])
    info_df.drop (columns=['index', 'null'], axis=1, inplace=True)
    #st.dataframe(info_df) #get_df_info(df)
    return info_df

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
   
def column_name(term: str) -> str:
    try:
        ret_val = key_values.get(term)
    except:
        ret_val = term
    return ret_val

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    Args:
        df (pd.DataFrame): Original dataframe
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    #modification_container = st.container()
    modification_container = st.sidebar.container()
    #st.sidebar.selectbox
    with modification_container:
        with st.popover("DataSource infos"):
            #st.markdown("Hello World 👋")
            st.dataframe(get_df_info(df))
        to_filter_columns = st.multiselect("Filter dataframe on", 
                                            options=df.columns, 
                                            format_func=lambda x: "{}".format(key_values.get(x),x)
                                          )
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df

data_url = 'https://api.gouv.fr/api/v1/apis'
response = requests.get(data_url).json()
df = pd.DataFrame(response)

df["logo"] = df["logo"].apply(smi_to_png)
df["path"] = df["path"].apply(smi_to_png)
df["openness"] = df["openness"].apply(smi_to_status)
    
df_display=filter_dataframe(df)
#lambda x: "{}".format(key_values.get(x),x)
#"title".format(key_values.get(x),x)

df = df.sort_values(by="owner", ascending=True)
#ss.df = df.copy

if "filters_options" not in st.session_state:
    #df = pd.DataFrame(response)
    df_display = df_display.sort_values(by="owner", ascending=True)
    st.session_state.filters_options = ""

height = (len(df_display) + 1) * 35 + 3


#buffer = io.StringIO()
#df_display.info(buf=buffer)
#s = buffer.getvalue()
#st.text(s)

st.dataframe(
  #data=df, 
  data=df_display, 
  #width=None, 
  height=height, 
  #height=None,
  #*, 
  use_container_width=True, 
  hide_index=True, 
  column_order=("logo","owner","title","openness","tagline","path","datapass_link","slug","owner_acronym","datagouv_uuid"), 
  column_config={
      "title": st.column_config.TextColumn(column_name("title")),
      "owner": st.column_config.TextColumn(column_name("owner")),
      "openness": st.column_config.TextColumn(column_name("openness")),
      "tagline": st.column_config.TextColumn(column_name("tagline")),
      "path": st.column_config.LinkColumn(column_name("path"), help="Official Details link"),
      "logo": st.column_config.ImageColumn(column_name("logo"), help="Owner's logo"),
      "datapass_link": st.column_config.LinkColumn(column_name("datapass_link"), help="Official link"),
      "slug": st.column_config.TextColumn(column_name("slug")),
      "owner_acronym": st.column_config.TextColumn(column_name("owner_acronym")),
      "datagouv_uuid": st.column_config.TextColumn(column_name("datagouv_uuid"))
  },  
  key=None, 
  on_select="ignore", 
  selection_mode="multi-row")


