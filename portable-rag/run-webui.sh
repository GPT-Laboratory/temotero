#!/bin/sh
pip install -r requirements.txt -qq
streamlit run main.py --client.toolbarMode=viewer -- -i data/pilot-v8/snowflake-arctic-embed2_paged -o data/pilot-v8/texts --servermode
