import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Page setting
st.set_page_config(page_title="AETS SUIVI", page_icon="favicon.png", layout="wide", initial_sidebar_state="auto", menu_items=None)

def get_region(value):
    if 'BELIER' in value.upper() or 'MORONOU' in value.upper():
        return 'Bélier-Moronou'
    elif 'CAVALLY' in value.upper() or 'GUEMON' in value.upper():
        return 'Cavally-Guémon'
    elif 'INDENIE-DJUABLIN' in value.upper() :
        return 'Indénié Djuablin'
    elif 'HAUT-SASSANDRA' in value.upper() or 'TONKPI' in value.upper():
        return 'Haut Sassandra - Tonkpi'
    elif 'LA ME' in value.upper():
        return 'La Mé'
    elif 'LOH-DJIBOUA' in value.upper():
            return 'Loh-Djiboua'
    elif 'SAN-PEDRO' in value.upper():
        return 'San Pedro'
    elif 'NAWA' in value.upper():
        return 'Nawa'
    else:
        return None
objectifs = {
    'Bélier-Moronou': 7313,
    'Cavally-Guémon': 7400,
    'Haut Sassandra - Tonkpi': 14700,
    'Indénié Djuablin': 7315,
    'La Mé': 7400,
    'Loh-Djiboua': 11800,
    'Nawa': 7300,
    'San Pedro': 11200
    }

objectifs_CO = {
    'CAEK': 1300,
    'CAEVA': 2700,
    'CAGG': 2000,
    'COANI': 400,
    'CODERLACS': 6000,
    'COOP -CA NECAB': 2100,
    'COOP CA NOBIELTO': 1900,
    'SCOOPS COOPAA': 2400,
    'COOPALBA': 1500,
    'COOPAOU': 1200,
    'COOP-CA-ABOTRE': 3100,
    'COOPROYA': 2500,
    'ECAMOG': 4000,
    'ECOPADI': 2900,
    'ECSP': 4100,
    'LAFI BEBE DE MAN': 1500,
    'SAMA.H.S.SCOOPS': 4700,
    'SCAANIAS': 2300,
    'SCAMG': 2400,
    'SCASOU': 2000,
    'SCOOPRADI': 2000,
    'SCOOPS CADT': 3300,
    'SNCC-SCOOPS': 2500,
    'SCOOPS-CA.MO.BIAN': 2500,
    'SCSPA': 1700,
    'SOCABB': 2900,
    'SOCAGS': 1500,
    'SOCAS CA': 5000,
    'SOCOPDAL SCOOPS': 2000
}

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.image(Image.open('ates.png'),width=100)
z1, z2= st.columns(2)
with z1:
    st.title(":green[Choisissez le fichier de données:]")
with z2:
    uploaded_files = st.file_uploader(":blue[Choisissez le fichier de données:]",accept_multiple_files=True,type=["xlsx", "xls"],label_visibility='hidden')

if uploaded_files is not None:
    if len(uploaded_files) ==0 :
        st.info("Cette application vous permet suivre les statistiques de collecte.", icon="ℹ️")
    else:
        try:
            uploaded_file = uploaded_files[0]
            df = pd.read_excel(uploaded_file)
            
            df['Equipe'] = df['Région'].apply(get_region)
            nouvelles_colonnes = {'VIII_Q35a: Nombre de plants reçus: Depuis le début des distributions ? (Cohorte 2020-2021)': 'Nombre de plants reçus', 'VIII_Q35b: Nombre de plants effectivement plantés': 'Nombre de plants plantés','I_Q1: Nom et prénoms du répondant':'Nombre de producteurs'}
            df = df.rename(columns=nouvelles_colonnes)
            df.loc[df["_id"] == 249698465, "Nombre de plants reçus"] = 120
            df.loc[df["_id"] == 249698524, "Nombre de plants plantés"] = 60
            df.loc[df["_id"] == 249578302, "Nombre de plants plantés"] = 20


            # Créer un DataFrame avec les colonnes pertinentes pour le suivi journalier

            suivi_journalier = df[['Equipe', 'Nombre de plants reçus', 'Nombre de plants plantés', 'Nombre de producteurs']]
            colonne = list(set(suivi_journalier.columns.to_list()) - set(['Equipe']))
            count_columns = ['Nombre de producteurs']
            sums_columns = [col for col in suivi_journalier.columns if col not in count_columns]
            agg_functions = {col: 'sum' if col in sums_columns else 'count' for col in colonne}

            # Grouper par région, département et sous-préfecture et compter le nombre de producteurs et de coopératives uniques
            tableau_repartition = suivi_journalier.groupby(['Equipe']).agg(agg_functions)

            tableau_repartition = suivi_journalier.groupby('Equipe', as_index=False).agg(agg_functions)
            tableau_repartition['progression'] = (tableau_repartition['Nombre de plants reçus'] / tableau_repartition['Equipe'].map(objectifs)) * 100
            tableau_repartition['progression']  = tableau_repartition['progression'].apply(lambda x: '{:.2f}%'.format(x))
            tableau_repartition['Nombre de plants reçus'] = tableau_repartition['Nombre de plants reçus'].apply(lambda x: '{:.0f}'.format(x))
            tableau_repartition['Nombre de plants plantés'] = tableau_repartition['Nombre de plants plantés'].apply(lambda x: '{:.0f}'.format(x))

            # Créer une colormap de dégradé de bleu
            def color_cell(val):
                if val <= 0.20:
                    color = 'background-color: #aaf6aa'  # Couleur de la cellule
                if val <= 0.40:
                    color = 'background-color: #8ece8e'  # Couleur de la cellule
                if val <= 0.60:
                    color = 'background-color: #74ab74'  # Couleur de la cellule
                if val <= 0.80:
                    color = 'background-color: #508c50'  # Couleur de la cellule
                else:
                    color = 'background-color: #337f33'  # Couleur de la cellule
                return color
            def cooling_highlight(val):
                color = '#aaf6aa' if val else 'white'
                return f'background-color: {color}'


            # Affichage du tableau avec Streamlit

            st.markdown("<h1 style='text-align: center;color: green;'>TABLEAU DE SUIVI PAR ZONES</h1>", unsafe_allow_html=True)
            st.table(tableau_repartition.style.applymap(cooling_highlight,subset=['progression']))



            # Créer un DataFrame avec les colonnes pertinentes pour le suivi journalier
            suivi_journalier_CO = df[['Equipe', 'Nombre de plants reçus', 'Nombre de plants plantés', 'Nombre de producteurs','Nom de la coopérative']]
            colonne = list(set(suivi_journalier_CO.columns.to_list()) - set(['Equipe','Nom de la coopérative']))
            count_columns = ['Nombre de producteurs']
            sums_columns = [col for col in suivi_journalier_CO.columns if col not in count_columns]
            agg_functions = {col: 'sum' if col in sums_columns else 'count' for col in colonne}

            # Grouper par région, département et sous-préfecture et compter le nombre de producteurs et de coopératives uniques
            #tableau_repartition = suivi_journalier_CO.groupby(['Equipe','Nom de la coopérative']).agg(agg_functions)

            tableau_repartition_CO = suivi_journalier_CO.groupby(['Equipe','Nom de la coopérative'], as_index=False).agg(agg_functions)
            tableau_repartition_CO['progression'] = (tableau_repartition_CO['Nombre de plants reçus'] / tableau_repartition_CO['Nom de la coopérative'].map(objectifs_CO)) * 100
            tableau_repartition_CO['progression']  = tableau_repartition_CO['progression'].apply(lambda x: '{:.2f}%'.format(x))
            st.markdown("<h1 style='text-align: center;color: green;'>TABLEAU DE SUIVI PAR COOPERATIVES</h1>", unsafe_allow_html=True)
            tableau_repartition_CO['Nombre de plants reçus'] = tableau_repartition_CO['Nombre de plants reçus'].apply(lambda x: '{:.0f}'.format(x))
            tableau_repartition_CO['Nombre de plants plantés'] = tableau_repartition_CO['Nombre de plants plantés'].apply(lambda x: '{:.0f}'.format(x))
            st.table(tableau_repartition_CO.style.applymap(cooling_highlight,subset=['progression']))                       
        except :
        #except Exception as e:
        # Affiche l'erreur complète dans Streamlit
            #st.exception(e)
            st.warning("Il semble que le fichier n'est pas conforme. S'il vous plaît, veuillez réessayer. ", icon="⚠️")

footer="""<style>
    a:link , a:visited{
    color: blue;
    background-color: transparent;
    text-decoration: underline;
    }

    a:hover,  a:active {
    color: red;
    background-color: transparent;
    text-decoration: underline;
    }

    .footer {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100%;
    background-color: white;
    color: black;
    text-align: center;
    }
</style>
<div class="footer">
    <p>Developed with ❤ by <a style='display: block; text-align: center;' href="https://www.linkedin.com/in/nsi%C3%A9ni-kouadio-eli%C3%A9zer-amany-613681185" target="_blank">Nsiéni Amany Kouadio</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)