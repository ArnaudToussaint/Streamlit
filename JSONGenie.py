# Import python packages sqlparse snowflake-snowpark-python streamlit
# For this streamlit to work, I am assuming you have 
# a database called JSON_GENIE_DB, and stage called JSON_GENIE_DB.PUBLIC.SAMPLES 
# and a json file format called JSON_GENIE_DB.PUBLIC.JSON_GENIE_FILE_FORMAT. 
# CREATE OR REPLACE FILE FORMAT JSON_GENIE_FILE_FORMAT
#	TYPE = JSON
#	NULL_IF = ()
#;
# The only thing that you need is to upload some sample files into the JSON_GENIE_DB.PUBLIC.SAMPLES stage.

import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, lit, concat_ws
from snowflake.snowpark.files import SnowflakeFile
from snowflake.snowpark._internal.analyzer.analyzer_utils import quote_name_without_upper_casing
from snowflake.snowpark._internal.utils import generate_random_alphanumeric

import sqlparse
import json
import pandas as pd


ROOT = "▶️"
SEP="➖"
EXP="💢"



def pretty_print_sql(sql):
    formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
    return formatted_sql

session = Session.builder.getOrCreate()
st.set_page_config(layout="wide")


@st.cache_data
def get_databases():
    return ["(none)"] + [x[0] for x in session.table("INFORMATION_SCHEMA.DATABASES").select("DATABASE_NAME").collect()]

@st.cache_data
def get_schemas(database_name):
    return ["(none)"] + [x[0] for x in session.table("INFORMATION_SCHEMA.SCHEMATA").where(col("CATALOG_NAME")==lit(database_name)).select("SCHEMA_NAME").collect()]

@st.cache_data
def get_tables(database_name,schema_name):
    return ["(none)"] + [x[0] for x in session.table("INFORMATION_SCHEMA.TABLES")
                         .where((col("TABLE_CATALOG")==lit(database_name)) & 
                                (col("TABLE_SCHEMA")==lit(schema_name)) ).select("TABLE_NAME").collect()
                        ]



# Write directly to the app
st.title("JSON GENIE 🧞")

# COPY THE URL FOR THE STAGE YOU PROVISIONED FOR SAMPLE FILES
st.markdown("""
[Upload your sample files here](https://app.snowflake.com/organization/account/#/data/databases/JSON_GENIE_DB/schemas/PUBLIC/stage/SAMPLES) ⬅️ 
""")

files = ["(NONE)"] + [x[0] for x in session.sql("LIST @SAMPLES")[['"name"']].collect()]

selected = st.selectbox("Select a sample file", files)
if selected == "(NONE)":
    st.stop()

path = "@"+ selected
#st.write(path)
bytes = session.file.get_stream(path).read()
data = json.loads(bytes)
st.write(data)

def identify_type(obj):
    if isinstance(obj, str):
        return "string"
    elif isinstance(obj, int):
        return "int"
    elif isinstance(obj, float):
        return "float"
    elif isinstance(obj, list):
        return "array"
    elif isinstance(obj, dict):
        return "variant"
    else:
        return "string"

def generate_code(columns, source_column, source_table):
    new_columns  = []
    new_explodes = []
    final_code = ""
    for index, c in columns.iterrows():
        data_path = c["data_path"]
        alias     = c["alias"]
        type      = c["type"]
        new_explode = c["explode"] if "explode" in c else None
        if not pd.isna(new_explode):
            new_explode_expr = f"{new_explode} {c['explode_prefix']}"
            if not new_explode_expr in new_explodes:
                new_explodes.append(new_explode_expr)
        new_columns.append(f"{data_path}::{type} as {alias} ")
    final_code = "SELECT \n " + ",\n ".join(new_columns) + " \n FROM " + source_table
    if new_explodes:
        final_code =  final_code + ",\n "
        final_code = final_code + ",\n".join(new_explodes)
    final_code = final_code.replace("@@SRC@@",source_column)
    final_code = final_code.replace("@@SRCTABLE@@",source_table)
    return final_code

columns = st.session_state.get("columns",pd.DataFrame())

if columns.empty:
    columns = pd.DataFrame([
        {"path":ROOT, 
         "alias":"root", 
         #"data":data,
         "type":identify_type(data),
         "data_path":"@@SRC@@",
         "selected":False,
         "targets":""}
    ])
    if "data_dict" not in st.session_state:
        st.session_state["data_dict"] = {ROOT:data}
    


select_columns = st.data_editor(columns,column_order=["path","alias","type","selected","targets"],
               disabled=["path"],use_container_width=True)


# Method to remove rows where selected=True and reset index
def remove_selected_rows(df):
    df = df[df['selected'] == False]
    df = df.reset_index(drop=True)
    return df

def expand_row(row):
    data_dict = st.session_state.data_dict
    row_data  = data_dict[row["path"]]
    new_rows = []
    if isinstance(row_data,list):
        path  = row["path"]  + EXP + "INDEX"
        alias = row["alias"] + "_INDEX"
        explode_prefix = "EXP" + generate_random_alphanumeric(5)
        data_path = explode_prefix + ".INDEX"
        explode = f"TABLE(FLATTEN({row['data_path']})) "
        new_rows.append({
            "path" : path,
            "alias": alias,
            "type" : "int",
            "data" : None,
            "data_path":data_path,
            "selected":False,
            "explode": explode,
            "explode_prefix":explode_prefix
            })
        path  = row["path"]  + EXP + "VALUE"
        alias = row["alias"] + "_VALUE"

        element_type   = identify_type(row_data[0]) if len(row_data) else "variant"
        element_sample = row_data[0] if len(row_data) else {}
        data_path = explode_prefix + ".VALUE"
        new_rows.append({
            "path" : path,
            "alias": alias,
            "type" : element_type,
            "data" : element_sample,
            "data_path":data_path,
            "selected":False,
            "explode": explode,
            "explode_prefix":explode_prefix
            })
        data_dict[path] = element_sample
    else:
        for key in row_data.keys():
            path = row["path"] + SEP + key
            data = row_data[key]
            data_dict[path] = data
            alias = row["alias"] + "_" + key if row["path"] != ROOT else key
            data_path = row["data_path"] + ":" + quote_name_without_upper_casing(key)
            explode = row["explode"] if "explode" in row else None
            new_rows.append({
            "path" : path,
            "alias": alias,
            "type" : identify_type(data),
            "data" : data,
            "data_path":data_path,
            "selected":False,
            "explode": explode,
            "explode_prefix":row["explode_prefix"] if "explode_prefix" in row else None
            })
    return pd.DataFrame(new_rows)

    
    
# Function to process the DataFrame
def process_dataframe(df,flag="none"):
    new_df = pd.DataFrame(columns=df.columns)
    for index, row in df.iterrows():
        if (row['selected'] or flag=="all") and (row["type"] in ["array","variant"]):
            st.write(row['type'])
            new_rows = expand_row(row)
            new_df = pd.concat([new_df, new_rows], ignore_index=True)
        else:
            new_df = pd.concat([new_df, pd.DataFrame([row])], ignore_index=True)
    return new_df

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("↕️ expand row"):
       if select_columns["selected"].any():
           st.session_state.columns = process_dataframe(select_columns)
           st.rerun()
       else:
           st.warning("No rows selected")
with col2:
    if st.button("❌ remove rows"):
       #select_columns["selected"].any() and
       st.session_state.columns = remove_selected_rows(select_columns)
       st.rerun()
with col3:
    if st.button("update rows"):
        st.session_state.columns = select_columns
        st.rerun()
    if st.button("expand_all"):
        while True:
            before_count = len(select_columns)
            select_columns = process_dataframe(select_columns,"all")
            after_count = len(select_columns)
            if after_count > before_count:
                pass
            else:
                break
        st.session_state.columns = select_columns
        st.rerun()
        


def generate_query(source_table, source_column):
    new_columns = []
    for c in columns:
        quoted_parts = [quote_name_without_upper_casing(x) for x in c.name.split(SEP)]
        path = source_column + ":" + ":".join(quoted_parts)
        new_columns.append(f"{path}::{c.type} as {c.alias} ")
    final_code = "SELECT \n " + ",\n ".join(new_columns) + " \n FROM " + source_table
    # add explodes
    #final_code = pretty_print_sql(final_code)
    return final_code

warehouses =[(x[0],x[3]) for x in session.sql("show warehouses").collect()]


streams_and_base_tables     = [(x[6], x[2]+"."+x[3] + "." + x[1]) for x in session.sql("show streams").collect()]



task_name     = st.text_input("task","TRIGERRED_TASK")
warehouse     = st.selectbox("warehouses",warehouses)
source_table_and_stream  = st.selectbox("source_table", streams_and_base_tables)
source_table  = source_table_and_stream[0]
stream        = source_table_and_stream[1]
source_column = st.text_input("source column","DATA")
target_table_database = None
target_table_schema = None
target_table_name = None
st.caption("target database")
col1, col2, col3 = st.columns(3)
with col1:
    target_table_database = st.selectbox("database",get_databases())
with col2:
    target_table_schema = st.selectbox("schema",get_schemas(target_table_database))
with col3:
    target_table_name  = st.text_input("table", "target_table")
target_table  = target_table_database + "."+target_table_schema+"."+ target_table_name




with st.expander("code"):
    final_code = generate_code(columns, source_column, stream)
    final_code = f""" 
CREATE OR REPLACE TASK {task_name}  WAREHOUSE = {warehouse[0]}
WHEN system$stream_has_data('{stream}')
AS
INSERT INTO {target_table}
{final_code};
    """
    
    st.code(final_code, "sql")
    
    if st.button("create task"):
        session.sql(final_code).count()
        st.success(f"Task {task_name} created")
    if st.button("sample data"):
        format="JSON_GENIE_FILE_FORMAT"
        prefix = "SRC" + generate_random_alphanumeric(5)
        source_table = "@" + selected + f" (FILE_FORMAT=>{format}) {prefix}"
        source_column = f"{prefix}.$1"
        test_code = generate_code(columns,source_column, source_table)
        st.write(session.sql(test_code))
    if st.button("create target table"):
        format="JSON_GENIE_FILE_FORMAT"
        prefix = "SRC" + generate_random_alphanumeric(5)
        source_table = "@" + selected + f" (FILE_FORMAT=>{format}) {prefix}"
        source_column = f"{prefix}.$1"
        test_code = generate_code(columns,source_column, source_table)
        session.sql(f"CREATE OR REPLACE TABLE {target_table} AS {test_code} LIMIT 0").count()
        st.success(f"Table {target_table} created")

    if st.checkbox("experimental INSERT MULTITABLE"):
        # Split the 'targets' column and create a list of lists
        split_targets = columns['targets'].str.split(',')
        split_targets = [x for x in split_targets if not isinstance(x,float)]
        # Flatten the list of lists to a single list
        flat_list = [item.strip() for sublist in split_targets for item in sublist]
        
        # Convert the list to a set to get unique values
        unique_targets = set(flat_list)
        
    
        test_code = generate_code(columns,source_column, source_table)
        into_groups = []
        df = columns.copy()
        # Fill null values in 'targets' with an empty string
        df['targets'] = df['targets'].fillna('')
        for target in unique_targets:
            # Filter rows where 'targets' contains 'target'
            filtered_df = df[df['targets'].str.contains(target)]
            aliases = filtered_df['alias'].tolist()
            into_groups.append(f"INTO {target} VALUES ({','.join(aliases)}) \n") 
        st.code(F"""
INSERT ALL
{"".join(into_groups)}
{test_code}""","sql")
