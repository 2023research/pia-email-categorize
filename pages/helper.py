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