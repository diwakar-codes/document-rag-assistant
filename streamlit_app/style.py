import streamlit as st

CUSTOM_CSS = """
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

h1, h2, h3 {
    color: #111318;
    font-weight: 600;
}

.stButton>button {
    border-radius: 6px;
    border: 1px solid #D0D3D9;
    background-color: #FFFFFF;
    color: #111318;
    font-weight: 500;
}

.stButton>button:hover {
    border-color: #2563EB;
    color: #2563EB;
}

div[data-testid="stMetric"] {
    background-color: #F4F5F7;
    border: 1px solid #E4E6EB;
    border-radius: 10px;
    padding: 14px 16px;
}

.app-card {
    background-color: #F9FAFB;
    border: 1px solid #E4E6EB;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    line-height: 1.6;
}

.app-caption {
    color: #5B6270;
    font-size: 0.9rem;
}
</style>
"""


def inject_style():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
