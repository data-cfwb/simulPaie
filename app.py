from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import base64

# Set the page layout to wide
st.set_page_config(layout="wide", page_icon="💁‍♂️", page_title="Simulateur de paie")

st.write(
    """
    <style>
    [data-testid="stMetricDelta"] svg {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([4, 1])
left.title("💁‍♂️ Simulateur de paie")

left.markdown("""
    Cette application permet de simuler la paie sur base du barème.
    """
)

right.image("https://avatars.githubusercontent.com/u/104143126?s=400&u=4378e8c74a05dc497c8956fa95fd910e64963feb", width=150)

df = pd.read_csv('./effectifs_echelles.csv')

index_df = pd.read_csv('./index_df_with_prediction.csv', sep=',')

#convert to datetime
index_df['valid_since'] = pd.to_datetime(index_df['valid_since'], format='%Y/%m/%d')
# convert to float
index_df['index'] = index_df['index'].astype(float)
# get index for current year
index_current_year = index_df[index_df['valid_since'] <= datetime.now()].iloc[-1]

index = index_current_year['index']
valid_from = index_current_year['valid_since'].strftime('%Y-%m-%d')

list_of_echelles = df['echelle'].unique()

# form with bareme and anciennete
with st.form(key="my_form"):
    col1, col2, col3 = st.columns(3)

    echelle = col1.selectbox("Echelles de bareme", list_of_echelles)
    anciennete = col2.selectbox("Ancienneté", df['anciennete'].unique())
    etp = col3.number_input("ETP", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
    submit_button = st.form_submit_button(label="Calculer")

    if submit_button:
        # loc correct bareme from df
        bareme = df.loc[(df['echelle'] == echelle) & (df['anciennete'] == anciennete), 'bareme'].values[0]
    
        # calculate salary
        yearly_salary = round(bareme * index * etp, 2)
        monthly_salary = round(yearly_salary / 12, 2)

        df_echelle = df.loc[df['echelle'] == echelle, ['bareme', 'anciennete']]
        df_echelle['diff_anciennete'] = df_echelle['anciennete'] - anciennete
        df_echelle['year'] = datetime.now().year + df_echelle['diff_anciennete']

        # loop over rows with iterrows()
        for idx, row in df_echelle.iterrows():

            diff_anciennete = df_echelle.loc[idx, 'anciennete'] - anciennete

            # add index of the year of ['year'] to the dataframe
            year = df_echelle.loc[idx, 'year']
            current_day = int(datetime.now().strftime('%d'))
            current_month = int(datetime.now().strftime('%m'))
            index_year = index_df[index_df['valid_since'] <= datetime(year, current_month, current_day)].iloc[-1]
            df_echelle.loc[idx, 'index'] = index_year['index']


        # define index of df
        df_echelle.set_index('year', inplace=True)

        df_echelle['etp'] = etp
        df_echelle['indexed_salary'] = df_echelle['bareme'] * df_echelle['index'] * df_echelle['etp']

        # add daily salary
        df_echelle['daily_salary_cal_day'] = round(df_echelle['indexed_salary'] / 360 / etp, 2)
        df_echelle['daily_salary_business_day'] = round(df_echelle['indexed_salary'] / 220, 2)
        df_echelle['daily_salary_w_company_cost'] = round(df_echelle['indexed_salary'] / 360 * 1.385, 2)
    
        st.write(f"Index: {index}") 
        st.write(f"Valide depuis le {valid_from} (source: [BOSA](https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0))")
        # 
        col1, col2 = st.columns(2)

        current_date = datetime.now().strftime('%Y-%m-%d')

        col1.metric("Salaire brut mensuel", f"{monthly_salary} €", f"{yearly_salary} €/an")
        col2.metric(f"Index au {current_date}", f"{index}", f"Valide depuis le {valid_from}", delta_color="off")

        # show table
        st.dataframe(df_echelle)

       # download dataframe 
        csv = df_echelle.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        echelle_file = echelle.replace('/', '_')

        filename = f"{echelle_file}_anc_{anciennete}_etp{etp}_{current_date}.csv"

        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Télécharger le tableau</a>'
        st.markdown(href, unsafe_allow_html=True)



        st.markdown(f"""
            **Les hypothèses sont les suivantes:**
            - 1 an = 12 mois et 1 mois ;
            - 1 an = **220 jours ouvrables** ;
            - 1 journée = 7,60 heures ou **07h36** ;
            - les charges patronales sont estimée à **38,50 %** ;
            - l'index suit une courbe linéaire prédite à travers un modèle ARIMA (méthode décrite [ici](https://github.com/data-cfwb/simulPaie/blob/main/index_arima.ipynb))
            """)

        # rename columns
        df_echelle = df_echelle.rename(columns={'bareme': 'Barème salarial', 'anciennete': 'Ancienneté en années', 'indexed_salary': 'Salaire brut annuel indexé'})
        
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # create two independent figures with px.line each containing data from multiple columns
        fig = px.line()
        fig.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['Barème salarial'], name='Barème salarial')
        fig.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['Salaire brut annuel indexé'], name="Salaire brut annuel indexé")

        
        fig2 = px.line()
        
        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['daily_salary_cal_day'], name="Salaire brut journalier (calculé sur 360 jours)")
        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['daily_salary_business_day'], name="Salaire brut journalier (sur 220 jours)")
        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['daily_salary_w_company_cost'], name="Cout brut journalier (sur 220 jours avec les charges de l'entreprise)")

        fig2.update_traces(yaxis="y2")

        subfig.add_traces(fig.data + fig2.data)

        subfig.layout.xaxis.title="Ancienneté en années"
        subfig.layout.yaxis.title="Montants annuels en €"
        subfig.layout.yaxis2.title="Montants journaliers en €"

        subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

        # display legend outside of plot

        subfig.update_layout(showlegend=True, height=600, width=1000, legend=dict(
            yanchor="top",
            y=-0.2,
            xanchor="left",
            x=0.01
        ))


        subfig.add_vline(x=anciennete, line_width=1, line_dash="dash", line_color="green")

        
        st.plotly_chart(subfig, use_container_width=False)       

      
st.markdown("""
This app is a work in progress and has been made by the [Data Office](https://github.com/data-cfwb) of CFWB. 

Source code is available on [GitHub](https://github.com/data-cfwb/simulPaie/).
""")