import streamlit as st

import sys
from pathlib import Path
parent_path = str(Path(__file__).resolve().parent.parent.parent)  # /online_portfolio_selection
sys.path.append(parent_path)

st.set_page_config(
    page_title="Online Portfolio Selection",
    page_icon="👋",
)

st.write("# Welcome to Online Portfolio Selection! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ### Introduction 📚
    
    Online portfolio selection is a framework for designing investment strategies that adapt to changing market 
    conditions in real time. In this framework, an investor makes decisions about which assets to buy and sell based on
    historical and current market data, with the goal of maximizing returns while minimizing risk.

    ### Characteristics of Online Portfolio Selection
    - Based on patterns in the historical market data
    - Type of machine learning problem
    - Different applications in variety fields like finance, economics, and machine learning
    
    **👈 Select a demo from the sidebar** to see our Online Portfolio Selection backtesting! 🔥🔥
"""
)
