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
import os
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from streamlit.logger import get_logger


import yaml
from yaml.loader import SafeLoader

#############################################################################################
LOGGER = get_logger(__name__)
path_results = './results'

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

        if "issue_size" not in st.session_state:
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

            area = st.selectbox(
            "which area needs maintenance?",
            ('unclear',"bedroom", "living room"),
            # index=None,
            placeholder="Select area",
            disabled=disable,key='area'
            )

            location = st.selectbox(
            "which loction has issue?",
            ('unclear',"ceiling", "pool"),
            # index=None,
            placeholder="Select location",
            disabled=disable,key='location'
            )


            issue = st.selectbox(
            "which issue?",
            options=location_issue[location],
            # index=None,
            placeholder="Select issue",
            disabled=disable,key='issue'
            )

            maintenance_type = st.selectbox(
            "what maintenance requied?",
            options=issue_maintenance_type[issue],
            index=0,
            placeholder="Select issue",
            disabled=disable,key='maintenance_type'
            )

            # Every form must have a submit button.
            issue_str = is_maintenance+'/'+area+'/'+location+'/'+issue+'/'+maintenance_type
            if is_maintenance=='yes': 
                submitted = st.button("➕ Add issue",on_click=add_issue, args=(issue_str,))  

        #### showing issues###############
        for i in range(len(st.session_state.issue_list)):
            c1, c2 = st.sidebar.columns([0.3,0.7], gap='small')    
            if is_maintenance=='yes':        
                with c2:
                    st.write(st.session_state.issue_list[i])
                with c1:
                    st.session_state.deletes.append(st.button("❌", key=f"delete{i}", on_click=delete_field, args=(i,)))
        # st.write(issue_list)
        print ('st.session_state.issue_list',st.session_state.issue_list)
        # print ('st.session_state.issue_size',st.session_state.issue_size)

    ###### submit button##################################################################
         
        def reset():
            st.session_state.is_maintenance = 'no'
            st.session_state.area = 'unclear'
            st.session_state.location = 'unclear'
            st.session_state.issue = 'unclear'
            st.session_state.maintenance_type = 'unclear'            
            st.session_state.issue_size = 0
            st.session_state.issue_list = []
            st.session_state.deletes = []
        print (st.session_state.maintenance_type)

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
# test section

        # def add_field():
        #     st.session_state.fields_size += 1

        # def delete_field(index):
        #     st.session_state.fields_size -= 1
        #     del st.session_state.fields[index]
        #     del st.session_state.deletes[index]

        # # st.header("Dynamic form ⚒️")
        # # st.divider()

        # if "fields_size" not in st.session_state:
        #     st.session_state.fields_size = 0
        #     st.session_state.fields = []
        #     st.session_state.deletes = []

        # # fields and types of the table
        # for i in range(st.session_state.fields_size):
        #     c1, c2 = st.columns(2)
        #     with c1:
        #         st.session_state.fields.append(st.text_input(f"Field {i}", key=f"text{i}"))

        #     with c2:
        #         st.session_state.deletes.append(st.button("❌", key=f"delete{i}", on_click=delete_field, args=(i,)))

        # st.button("➕ Add field", on_click=add_field)
        
        
        

if __name__ == "__main__":
    run()


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

from typing import Any

import numpy as np

import streamlit as st
st.write("## Welcome to PIA email categorization!")
st.markdown(
    """
    Please follow the below steps:
    1. read the text body
    2. answer the questions in all selectboxs on the left sidebar. 
        - if a selectbox does not have option matching the text, please email the new option to shuming.liang@uts.eud.au. We will add the new option to that selectbox.
    3. after completed all answers, please click the submit button to save your answer.

"""
)