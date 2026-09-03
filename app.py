import streamlit as st
import datetime
from database import init_db, get_connection, get_analytics_summary
from models import save_user_profile, get_user_profile, add_body_metric, get_body_metrics
from training_engine import generate_workout, save_generated_workout
from safety import check_safety_guidelines

# 1. A configuração da página DEVE ser a primeira instrução do Streamlit
st.set_page_config(page_title="AI FIT ELITE", page_icon="⚡", layout="wide")

# 2. Inicialização do banco
init_db()

# 3. Carregamento de dados e elementos da barra lateral
profile = get_user_profile()

st.sidebar.title("⚡ AI FIT ELITE")
