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
import streamlit.components.v1 as components
from streamlit_modal import Modal
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

issue_maintype = {
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
        df = pd.read_csv('./data/b00.csv',sep=',')
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

# def run():

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
    col1, col2,col3 = st.columns([0.4,0.3,0.3])
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
    def add_issue(issue_str=None):
        if issue_str !=None and issue_str not in st.session_state.issue_list:
            st.session_state.issue_list.append(issue_str)

    def delete_field(index):
        del st.session_state.issue_list[index]
        del st.session_state.deletes[index]
    def reset_no():
        if st.session_state.is_maintenance == 'no':
            st.session_state.key_area = 'unclear'
            st.session_state.key_location = 'unclear'
            st.session_state.key_issue = 'unclear'
            st.session_state.key_maintype = 'unclear'
            st.session_state.key_subtype = None   

    if "issue_list" not in st.session_state:
        st.session_state.issue_list = []
        st.session_state.deletes = []
    
    
    # st.sidebar.divider()
    is_maintenance = st.sidebar.selectbox( "Is it related to the property maintenance?", ("no","yes"), 
                                            placeholder="Select yes or no...", key='is_maintenance',on_change =reset_no)   
    disable = False if is_maintenance=='yes'else True

    def select_issues(label='0',opt=['0','1'],idx=0,phld="",disable=disable,key=['0','1']):
        opt.append('add a new option')
        c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
        with c1:
            item = st.selectbox(label=label, options=opt, index=idx, placeholder=phld, disabled=disable, key=key[0])           
        with c2:                
            disable_newopt = (item!="add a new option") or (disable)
            new_option = st.text_input(label="Input your new option",label_visibility='visible', placeholder='Input your new option',
                                        disabled = disable_newopt,key=key[1])  
            item = new_option if item=="add a new option" else item 
        return item 
    
    area = select_issues("which room or area has issue?",['unclear',"bedroom", "living room"],disable=disable,key=['key_area','key_area_new'])
    location = select_issues("what has issue?",['unclear',"ceiling", "pool"],disable=disable,key=['key_location','key_location_new'])
    issue = select_issues("which issue?",location_issue[location],disable=disable,key=['key_issue','key_issue_new'])
    maintype = select_issues("what maintenance requied?",issue_maintype[issue],disable=disable,key=['key_maintype','key_maintype_new'])
    subtype = select_issues("more maintenance requied?",issue_maintype[issue],idx=None,disable=disable,key=['key_subtype','key_subtype_new'])
    print ('st.session_state.key_area',st.session_state.key_area)

    

######## add issue description ###########################
    opt_long_checklist=[]
    issue_str=""
    for ele in [is_maintenance,area,location,issue,maintype,subtype]:  
        if ele !=None:
            if len(ele)>20:
                opt_long_checklist.append(ele)
        issue_str=issue_str+ele+'/' if ele !=None else issue_str+'None/'
    print (issue_str)

    ### add issue button ##########
    
    bool_addissue = disable
    if  "add a new option" in [st.session_state.key_area, st.session_state.key_location, st.session_state.key_issue,
                               st.session_state.key_maintype, st.session_state.key_subtype]:
        bool_addissue = True
    bool_addopt = (not bool_addissue) or (is_maintenance=='no') 
    c1, c2 = st.sidebar.columns([0.6,0.4], gap='small') 
    with c1:
        add_issue_res = st.button("➕ Add issue", on_click=add_issue, args=(issue_str,),disabled=bool_addissue, key='add_issue')  
    with c2:
        add_new_options_res = st.button("➕ Add new option", disabled=bool_addopt, key='add_new_options')

        my_modal = Modal(title='', key='key_add_newopt_modal',padding=0,max_width=600,)
        if 'confirm' not in st.session_state:
            st.session_state.confirm = False
        def modal_save_newopt():       
            st.session_state.confirm = True
        # def modal_close():
        #     my_modal.close()
        print ('add_new_options_res',add_new_options_res)
        if add_new_options_res:
            # st.error("Do you really, really, wanna do this?")
            # if st.button("Yes I'm ready to rumble"):
            #     st.button('Confirm to save it (red) to system',key='add_newopt_confirm_key')
            if len(opt_long_checklist) > 0:
                with my_modal.container():                
                    # st.markdown(f'''Your new option :red[{opt_long_checklist}] is too long, please use short key words.''') 
                    html_string = f'''
                    <p><center>Your new option as below is too long, please use a short key-words.</center></p>
                    <h3><center> {opt_long_checklist}</center></h3>               
                    <script language="javascript">
                    document.querySelector("h3").style.color = "red";
                    </script>
                    '''
                    components.html(html_string)
                    st.button('Back to re-edit it', key='key_add_newopt_revise')
            else:
                with my_modal.container():                
                    html_string = f'''
                    <p><center>Your new issue and maintenance description is</center></p>
                    <h3><center>{issue_str}</center></h3>
                    <p><center>Please confirm to save it as an new option into the system or back to edit it.</center></p>                
                    <script language="javascript">
                    document.querySelector("h3").style.color = "red";
                    </script>
                    '''
                    components.html(html_string)
                    # st.markdown('''
                    # :red[Streamlit] :orange[can] :green[write] :blue[text] :violet[in]
                    # :gray[pretty] :rainbow[colors].''') on_click= modal_close
                    st.button('Back to re-edit it', key='key_add_newopt_revise')
                    st.button('Confirm to save it to system',on_click=modal_save_newopt, key='key_add_newopt_confirm')

                

######## showing issues###############################################
    st.sidebar.divider()
    for i in range(len(st.session_state.issue_list)):
        c1, c2 = st.sidebar.columns([0.2,0.8], gap='small')    
        if is_maintenance=='yes':                    
            with c1:
                st.session_state.deletes.append(st.button("❌", key=f"delete{i}", on_click=delete_field, args=(i,)))
            with c2:
                st.write(st.session_state.issue_list[i])
    # st.write(issue_list)
    print ('st.session_state.issue_list',st.session_state.issue_list)

###### submit button##################################################################
        
    
    def reset():
        st.session_state.is_maintenance = 'no'
        st.session_state.key_area = 'unclear'
        st.session_state.key_location = 'unclear'
        st.session_state.key_issue = 'unclear'
        st.session_state.key_maintype = 'unclear'    
        st.session_state.key_subtype = None 
        st.session_state.issue_list = []
        st.session_state.deletes = []

    st.sidebar.divider()
    st.markdown("""
            <style>
            div.stButton {text-align:center}
            </style>""", unsafe_allow_html=True)
    submit = st.sidebar.button(label="Final submit",on_click=reset)    
    
    if submit:            
        df = pd.DataFrame([[id_email,is_maintenance,area,location,issue,maintype]],columns=['id_email','is_maintenance','area','location','issue','maintype'])
        print (df)
        df.to_csv(os.path.join(path_results,id_email+'.csv'),index=False)
        st.rerun()

    # if not submit and is_maintenance is not None:
    st.sidebar.write("Please do not forget to submit your results before annotating next one",submit)
##########################################################################################################################################################
##########################################################################################################################################################


# if __name__ == "__main__":
#     run()

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