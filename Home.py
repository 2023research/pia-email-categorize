# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from urllib.error import URLError
import os, psycopg2
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from streamlit.logger import get_logger


import yaml
from yaml.loader import SafeLoader

#############################################################################################
LOGGER = get_logger(__name__)
path_results = './results'
#############################################################################################
# database
def connect_db():
    conn = psycopg2.connect("dbname=pia host=piadb.c4j0rw3vec6q.ap-southeast-2.rds.amazonaws.com user=postgres password=UTS-DSI2020")
    return conn.cursor()
# create schema####
def create_grant_schema(schema):
    cur = connect_db()
    print (cur)
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema} AUTHORIZATION postgres ")
    cur.execute(f"GRANT CREATE, USAGE ON SCHEMA {schema} TO postgres")
    cur.execute(f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO postgres")
    cur.execute(f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {schema} TO postgres")
    cur.execute("COMMIT")
# create_grant_schema('email')
## create table###############
def create_table_issue():
    sql = """CREATE TABLE IF NOT EXISTS email.issues (
        area varchar(1450) NOT NULL,
        location varchar(1450) NOT NULL,
        issue varchar(1450) NOT NULL,
        maintype varchar(1450) NOT NULL,
        subtype varchar(1450) NOT NULL,
        subsubtype varchar(1450) NOT NULL,
        subsubsubtype varchar(1450) NOT NULL,
        note varchar(1450) NOT NULL
        )"""
    cur = connect_db()
    cur.execute(sql)
    cur.execute("COMMIT")
# create_table_issue()
########################################################################################################
# body
location_issue={
    'ceiling':['unclear','crack','paint'],
    'pool':['unclear','water','wall crack'],
    'unclear':['unclear','light','rubbish','general'],    
}

issue_maintenance_type = {
    'unclear':['unclear','handyman'],
    'crack':['unclear','gyprock'],
    'paint': ['unclear','painting'],
    'light': ['unclear','electrian'],
    'rubbish': ['unclear','cleaner'],
    'general': ['unclear','handyman'],
    'water':['unclear','...'],
    'wall crack':['unclear','...']
}

def read_email(sample=False):
    files = [f[:-4] for f in os.listdir(path_results)] 
    @st.cache_data
    def get_email_data():
        df = pd.read_csv('./data/b14.csv')
        print('######################')
        return df   
    try:
        # print (files)
        df = get_email_data()
        df = df[['Body','ID']]
        df_bool = df['ID'].apply(lambda x: x not in files)
        df_out = df[df_bool]
        if df_out.shape[0]<10:
            st.markdown(
            """
            ## **only less than 10 email samples need to be annotated, please inform UTS team to unpdate dataset by sending email: shuming.liang@uts.edu.au  thanks very much**
        """
        )
        # if sample:
        #     df = df.sample()           
        # else:
        #     df = df.iloc[0:2]
            
        return df_out.iloc[0]['Body'],df_out.iloc[0]['ID']
        
    except URLError as e:
        st.error(
            """
            **The email content cannot be loaded correctly, please send this error message to email: shuming.liang@uts.edu.au**
            Connection error: %s
        """
            % e.reason
        )

def run():
    
    ############################################################################################
    #authorization
    # usernames = ['john','james','oliver','david','emma','alex']
    # passwords = ['8963','2836', '4936','3232','6323','8768']

    # hashed_passwords = stauth.Hasher(['8963','2836', '4936','3232','6323','8768']).generate()
    # print (hashed_passwords)


    with open('./login.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )
    name, authenticator_status, username = authenticator.login('Login','main')
    if authenticator_status==False:
        st.error('username/password is incorrect')
    elif authenticator_status==None:
        st.warning("please enter your username and password")
    else:  
        # st.set_page_config(
        #     page_title="Hello",
        #     page_icon="👋",
        # )    
        col1, col2 = st.sidebar.columns([1, 1,])
        with col1:
           st.subheader(f'Welcome {name}')
        with col2:
            authenticator.logout('Logout')
        # st.sidebar.divider()
    #########body######################################################################################
        # body
        
        


    #####load email #########################
        text_email,id_email = read_email()
        print (id_email)    
        st.header('Text to analyze', divider='red')
        st.markdown(text_email)
        st.header(body='',divider='red' )
        st.header('End')

    #### add issue ###############################   
        def add_issue(issue_str):
            if issue_str not in st.session_state.issue_list:
                st.session_state.issue_list.append(issue_str)

        def delete_field(index):
            del st.session_state.issue_list[index]
            del st.session_state.deletes[index]

        if "issue_list" not in st.session_state:
            st.session_state.issue_list = []
            st.session_state.deletes = []
        
        
        st.sidebar.divider()
        with st.sidebar:#.form("my_form"):
            # issue selction
            is_maintenance = st.sidebar.selectbox(
            "Is it related to the property maintenance?",
            ("no","yes"),
            # index=None,
            placeholder="Select yes or no...",
            disabled=False,key='is_maintenance'
            )   
            # print(is_maintenance)
            disable = False if is_maintenance=='yes'else True
            # print(int(disable))

            def select_issues(label='0',opt=['0','1'],phld="",disable=disable,key=['0','1']):
                opt.append('add a new option')
                c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
                with c1:
                    item = st.selectbox(label=label, options=opt, index=0, placeholder=phld, disabled=disable, key=key[0])           
                with c2:                
                    new_option = st.text_input(label="Input your new option",label_visibility='visible', placeholder='Input your new option',
                                               disabled = (item!="add a new option"),key=key[1])  
                    item = new_option if item=="add a new option" else item 
                return item
            area = select_issues("which room or area has issue?",['unclear',"bedroom", "living room"],disable=disable,key=['area','area_new'])
            location = select_issues("what has issue?",['unclear',"bedroom", "living room"],disable=disable,key=['location','location_new'])
            issue = select_issues("which issue?",location_issue[location],disable=disable,key=['issue','issue_new'])
            maintenance_type = select_issues("what maintenance requied?",issue_maintenance_type[issue],disable=disable,key=['maintenance_type','type_new'])

            # c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
            # with c1:
            #     area = st.selectbox("which room or area has issue?", ('unclear',"bedroom", "living room","add a new option"),
            #     placeholder="Select area", disabled=disable,key='area') # index=None            
            # with c2:                
            #     new_option = st.text_input(label="Input your new option",label_visibility='visible', placeholder='input your new option',disabled = (area!="add a new option"),key='area_new')  
            #     area = new_option if area=="add a new option" else area 

            # c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
            # with c1:
            #     location = st.selectbox("what has issue?",('unclear',"ceiling", "pool"), 
            #     placeholder="Select what", disabled=disable,key='location')
            # with c2:
            #     new_option = st.text_input(label="input your new option",label_visibility='visible', placeholder='input your new option',disabled = (location!="add a new option"),key='location_new')
            #     area = new_option if area=="add a new option" else area

            # c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
            # with c1:
            #     issue = st.selectbox( "which issue?", options=location_issue[location], placeholder="Select issue", disabled=disable,key='issue')
            # with c2:
            #     new_option = st.text_input(label="input your new option",label_visibility='visible', placeholder='input your new option',disabled = (issue!="add a new option"),key='issue_new')
            #     area = new_option if area=="add a new option" else area

            # c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
            # with c1:
            #     maintenance_type = st.selectbox( "what maintenance requied?", options=issue_maintenance_type[issue], 
            #     placeholder="Select maintenance", disabled=disable,key='maintenance_type')
            # with c2:
            #     new_option = st.text_input(label="input your new option",label_visibility='visible', placeholder='input your new option',disabled = (maintenance_type!="add a new option"), key='type_new')
            #     area = new_option if area=="add a new option" else area


    ######## add issue description ###########################
            issue_str = is_maintenance+'/'+area+'/'+location+'/'+issue+'/'+maintenance_type

            submitted = st.button("➕ Add issue", on_click=add_issue, args=(issue_str,),disabled=disable)  

    ######## showing issues###############################################
        st.sidebar.divider()
        for i in range(len(st.session_state.issue_list)):
            c1, c2 = st.sidebar.columns([0.3,0.7], gap='small')    
            if is_maintenance=='yes':        
                with c2:
                    st.write(st.session_state.issue_list[i])
                with c1:
                    st.session_state.deletes.append(st.button("❌", key=f"delete{i}", on_click=delete_field, args=(i,)))
        # st.write(issue_list)
        print ('st.session_state.issue_list',st.session_state.issue_list)

    ###### submit button##################################################################
         
        def reset():
            st.session_state.is_maintenance = 'no'
            st.session_state.area = 'unclear'
            st.session_state.location = 'unclear'
            st.session_state.issue = 'unclear'
            st.session_state.maintenance_type = 'unclear'     
            st.session_state.issue_list = []
            st.session_state.deletes = []

        st.sidebar.divider()
        submit = st.sidebar.button(label="Final submit",on_click=reset)    
       
        if submit:            
            df = pd.DataFrame([[id_email,is_maintenance,area,location,issue,maintenance_type]],columns=['id_email','is_maintenance','area','location','issue','maintenance_type'])
            print (df)
            df.to_csv(os.path.join(path_results,id_email+'.csv'),index=False)
            st.rerun()

        # if not submit and is_maintenance is not None:
        st.sidebar.write("Please do not forget to submit your results before annotating next one",submit)
##########################################################################################################################################################
##########################################################################################################################################################


if __name__ == "__main__":
    run()

############################################################################################################################
# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from typing import Any

# import numpy as np

# import streamlit as st
# st.write("## Welcome to PIA email categorization!")
# st.markdown(
#     """
#     Please follow the below steps:
#     1. read the text body
#     2. answer the questions in all selectboxs on the left sidebar. 
#         - if a selectbox does not have option matching the text, please email the new option to shuming.liang@uts.eud.au. We will add the new option to that selectbox.
#     3. after completed all answers, please click the submit button to save your answer.

# """
# )
############################################################################################################################

############################################################################