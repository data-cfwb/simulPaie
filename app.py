import streamlit as st
import pandas as pd
import plotly.express as px


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

index_df = pd.DataFrame({
    'valid_since': ['2022-06-01', '2022-09-01', '2023-01-01', '2024-01-01'], 
    'index': [1.8845, 1.9222, 2.1111, 2.2000],
    'status': ['active', 'active', 'estimation', 'estimation']
})

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

            if diff_anciennete > 0:
                df.loc[i, 'indexed_salary'] = round(df.loc[i, 'bareme'] * (1.01 ** diff_anciennete), 2)
            else:
                df.loc[i, 'indexed_salary'] = round(df.loc[i, 'bareme'], 2)

        st.write(f"Index: {index}") 
        st.write(f"Valide depuis le {valid_from}")
        # 
        col1, col2 = st.columns(2)
        col1.metric("Salaire brut annuel", f"{yearly_salary} €")
        col2.metric("Salaire brut mensuel", f"{monthly_salary} €")


        # get only columns bareme and anciennete
        df_echelle = df.loc[df['echelle'] == echelle, ['bareme', 'anciennete', 'indexed_salary']]
        
        # rename columns
        df_echelle = df_echelle.rename(columns={'bareme': 'Barème salarial', 'anciennete': 'Ancienneté en années', 'indexed_salary': 'Salaire brut annuel indexé'})
        
        # show the salary evolution
        fig = px.line(df_echelle, x="Ancienneté en années", y="Barème salarial", title="Evolution du barème salarial")

        # add new line for indexed salary
        fig.add_scatter(x=df_echelle['Ancienneté en années'], y=df_echelle['Salaire brut annuel indexé'], name="Salaire brut annuel indexé à 1% par année")

        # display legend
        fig.update_layout(showlegend=True, legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))


        # add vertical line
        fig.add_vline(x=anciennete, line_width=1, line_dash="dash", line_color="green")

        # add horizontal line
        fig.add_hline(y=yearly_salary, line_width=1, line_dash="dash", line_color="green")

        st.plotly_chart(fig, use_container_width=False)       

      


st.markdown("""
This app is a work in progress and has been made by the [Data Office](https://github.com/data-cfwb) of CFWB. 

Source code is available on [GitHub](https://github.com/data-cfwb/simulPaie/).
""")