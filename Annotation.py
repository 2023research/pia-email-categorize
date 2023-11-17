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
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)
path_results = '/workspaces/pia-email-categorize/results'

location_issue={
    'ceiling':['crack','paint'],
    'pool':['water','wall crack'],
    'unclear':['light','rubbish','general'],    
}

issue_maintenance_type = {
    'crack':['gyprock'],
    'paint': ['painting'],
    'light': ['electrian'],
    'rubbish': ['cleaner'],
    'general': ['handyman'],
    'water':['...'],
    'wall crack':['...']
}

def read_email():
    files = [f[:-4] for f in os.listdir(path_results)]
    def get_email_data():
        df = pd.read_csv('/workspaces/pia-email-categorize/data/b14.csv')
        return df
    try:
        print (files)
        df = get_email_data()
        df = df[['Body','ID']]
        df_bool = df['ID'].apply(lambda x: x not in files)
        df = df[df_bool]
        # print (df.columns)
        df = df.sample()
        return df.iloc[0]['Body'],df.iloc[0]['ID']
        
    except URLError as e:
        st.error(
            """
            **The email content cannot be loaded correctly, please send this error message to email: shuming.liang@uts.edu.au**
            Connection error: %s
        """
            % e.reason
        )
def write_result():
    a=0



def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    
    text_email,id_email = read_email()
    print (id_email)
    st.header('Text to analyze', divider='red')
    st.markdown(text_email)
    st.header(body='',divider='red' )
    st.header('End')

    is_maintenance = st.sidebar.selectbox(
    "Is this text related to the property maintenance?",
    ("yes", "no"),
    index=None,
    placeholder="Select yes or no...",
    disabled=False
    )   
    print(is_maintenance)
    disable = False if is_maintenance=='yes'else True
    print(int(disable))

    area = st.sidebar.selectbox(
    "which area needs maintenance?",
    ("bedroom", "living room","unclear"),
    index=None,
    placeholder="Select area",
    disabled=disable
    )

    location = st.sidebar.selectbox(
    "which loction has issue?",
    ("ceiling", "pool","unclear"),
    index=None,
    placeholder="Select location",
    disabled=disable
    )

    if location is None:
        location = 'unclear'

    issue = st.sidebar.selectbox(
    "which issue?",
    options=location_issue[location],
    index=None,
    placeholder="Select issue",
    disabled=disable
    )

    if issue is None:
        issue = 'general'

    maintenance_type = st.sidebar.selectbox(
    "what maintenance requied?",
    options=issue_maintenance_type[issue],
    index=None,
    placeholder="Select issue",
    disabled=disable
    )

    # submit button
    col1, col2 = st.sidebar.columns([1, 1,])
    with col1:
        submit = st.button(
        label="submit",
        )
    submit_re = submit
    with col2:
        next_text = st.button(
        label="annotate next one",
        )
    if submit:
        df = pd.DataFrame([[id_email,is_maintenance,area,location,issue,maintenance_type]],columns=['id_email','is_maintenance','area','location','issue','maintenance_type'])
        print (df)
        df.to_csv(os.path.join(path_results,id_email+'.csv'),index=False)
    if next_text:
        st.rerun()
    # if not submit and is_maintenance is not None:
    st.sidebar.write("Please do not forget to submit your results before annotating next one",submit,next_text,submit_re)
    

if __name__ == "__main__":
    run()
