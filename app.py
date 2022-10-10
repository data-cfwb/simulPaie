from datetime import datetime
import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(layout="centered", page_icon="💁‍♂️", page_title="Simulateur de paie")

left, right = st.columns([4, 1])
left.title("💁‍♂️ Simulateur de paie")

left.markdown("""
    Cette application permet de simuler la paie sur base du barème.
    """
)

right.image("https://avatars.githubusercontent.com/u/104143126?s=400&u=4378e8c74a05dc497c8956fa95fd910e64963feb", width=150)

df = pd.read_csv('./effectifs_echelles.csv')

index_df = pd.read_csv('./index_df.csv', sep=';')

#convert to datetime
index_df['valid_since'] = pd.to_datetime(index_df['valid_since'], format='%d/%m/%Y')
# convert to float
index_df['index'] = index_df['index'].str.replace(',', '.').astype(float)
# get index for current year
index_current_year = index_df[index_df['valid_since'] <= datetime.now()].iloc[-1]

index = index_current_year['index']
valid_from = index_current_year['valid_since'].strftime('%Y-%m-%d')

list_of_echelles = df['echelle'].unique()

# form with bareme and anciennete
with st.form(key="my_form"):
    col1, col2 = st.columns(2)

    echelle = col1.selectbox("Echelles de bareme", list_of_echelles)
    anciennete = col2.selectbox("Ancienneté", df['anciennete'].unique())
    etp = col1.number_input("ETP", min_value=0.0, max_value=1.0, value=1.0, step=0.05)
    submit_button = st.form_submit_button(label="Calculer")

    if submit_button:
        # loc correct bareme from df
        bareme = df.loc[(df['echelle'] == echelle) & (df['anciennete'] == anciennete), 'bareme'].values[0]

        # calculate salary
        yearly_salary = round(bareme * index * etp, 2)
        monthly_salary = round(yearly_salary / 12, 2)

        # add a column for indexed salary
        for i in range(len(df)):
            diff_anciennete = df.loc[i, 'anciennete'] - anciennete
            
            # multiply bareme with index
            df.loc[i, 'bareme'] = round(df.loc[i, 'bareme'] * index * etp, 2)

            df.loc[i, 'indexed_salary'] = round(df.loc[i, 'bareme'], 2)

            if diff_anciennete > 0:
                df.loc[i, 'indexed_salary'] = round(df.loc[i, 'bareme'] * (1.01 ** diff_anciennete), 2)

        # add daily salary
        df['daily_salary_cal_day'] = round(df['indexed_salary'] / 360, 2)
        df['daily_salary_business_day'] = round(df['indexed_salary'] / 220, 2)
        df['daily_salary_w_company_cost'] = round(df['indexed_salary'] / 360 * 1.385, 2)

        st.write(f"Index: {index}") 
        st.write(f"Valide depuis le {valid_from} (source: [BOSA](https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0))")
        # 
        col1, col2 = st.columns(2)
        col1.metric("Salaire brut annuel", f"{yearly_salary} €")
        col2.metric("Salaire brut mensuel", f"{monthly_salary} €")


        # get only columns bareme and anciennete
        df_echelle = df.loc[df['echelle'] == echelle, ['bareme', 'anciennete', 'indexed_salary']]
        
        # rename columns
        df_echelle = df_echelle.rename(columns={'bareme': 'Barème salarial', 'anciennete': 'Ancienneté en années', 'indexed_salary': 'Salaire brut annuel indexé'})
        
        subfig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # create two independent figures with px.line each containing data from multiple columns
        fig = px.line()
        fig.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['Salaire brut annuel indexé'], name="Salaire brut annuel indexé à 1% par année")
        fig.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['Barème salarial'], name='Barème salarial')
        # add vertical line

        fig2 = px.line()
        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df['daily_salary_cal_day'], name="Salaire brut journalier (calculé sur 360 jours)")
        # add scatter for day salary on other axis
        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df['daily_salary_business_day'], name="Salaire brut journalier (calculé sur 220 jours)")

        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df['daily_salary_business_day'], name="Salaire brut journalier (calculé sur 220 jours)")

        # add scatter for day salary
        fig2.add_scatter(x=df_echelle['Ancienneté en années'], y=df['daily_salary_w_company_cost'], name="Salaire brut journalier (calculé sur 220 jours avec les charges de l'entreprise)")

        fig2.update_traces(yaxis="y2")

        subfig.add_traces(fig.data + fig2.data)

        subfig.layout.xaxis.title="Ancienneté en années"
        subfig.layout.yaxis.title="Montants annuels en €"
        subfig.layout.yaxis2.title="Montants journaliers en €"
        # recoloring is necessary otherwise lines from fig und fig2 would share each color
        # e.g. Linear-, Log- = blue; Linear+, Log+ = red... we don't want this
        subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

       
        # display legend outside of plot

        subfig.update_layout(showlegend=True, height=800, legend=dict(
            yanchor="top",
            y=-0.99,
            xanchor="left",
            x=0.01
        ))


        subfig.add_vline(x=anciennete, line_width=1, line_dash="dash", line_color="green")

        
        st.plotly_chart(subfig, use_container_width=False)       

      
st.markdown("""
This app is a work in progress and has been made by the [Data Office](https://github.com/data-cfwb) of CFWB. 

Source code is available on [GitHub](https://github.com/data-cfwb/simulPaie/).
""")