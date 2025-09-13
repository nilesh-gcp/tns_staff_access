# config/config.py
import os
import streamlit as st

def get(section, key, default=None):
    return st.secrets.get(section, {}).get(key, default)