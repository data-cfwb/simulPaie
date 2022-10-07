import streamlit as st
import time
import datetime as dt
import humanize
import pandas as pd

humanize.i18n.activate("fr_FR")

st.set_page_config(layout="centered", page_icon="💁‍♂️", page_title="Simulateur de paie")

left, right = st.columns([4, 1])
left.title("💁‍♂️ Simulateur de paie")

left.markdown("""
    Cette application permet de simuler la paie sur base du barème.
    """
)

right.image("https://raw.githubusercontent.com/data-cfwb/.github/main/logo_data_office.png", width=150)

df = pd.read_csv('./effectifs_echelles.csv')

index = 1.9222
valid_from = "2022-09-01"

list_of_echelles = df['echelle'].unique()

# form with bareme and anciennete
with st.form(key="my_form"):
    col1, col2 = st.columns(2)

    echelle = col1.selectbox("Echelles de bareme", list_of_echelles)
    anciennete = col2.selectbox("Ancienneté", df['anciennete'].unique())
    submit_button = st.form_submit_button(label="Calculer")

    if submit_button:
        # loc correct bareme from df
        bareme = df.loc[(df['echelle'] == echelle) & (df['anciennete'] == anciennete), 'bareme'].values[0]

        # calculate salary
        yearly_salary = round(bareme * index, 2)
        monthly_salary = round(yearly_salary / 12, 2)

        # show the index and valid_from date 

        st.write(f"Index: {index}") 
        st.write(f"Valide depuis le {valid_from}")
        # 
        col1, col2 = st.columns(2)
        col1.metric("Salaire brut annuel", f"{yearly_salary} €")
        col2.metric("Salaire brut mensuel", f"{monthly_salary} €")


        # show the salary evolution
        st.subheader("Évolution du salaire")

        # get only columns bareme and anciennete
        df_echelle = df.loc[df['echelle'] == echelle, ['bareme', 'anciennete']]
        # use anciennete as index
        df_echelle = df_echelle.set_index('anciennete')

        # show the salary evolution
        st.line_chart(df_echelle)

        # add a point on the chart
 
      
        

      


st.markdown("""
This app is a work in progress and has been made by the [Data Office](https://github.com/data-cfwb) of CFWB. 

Source code is available on [GitHub](https://github.com/data-cfwb/reuNiote/).
""")