import streamlit as st
import pandas as pd
import numpy as np

import datetime
# from datetime import timedelta

# import matplotlib.pyplot as plt
# import seaborn as sns
# from matplotlib.ticker import FuncFormatter, MaxNLocator, FixedLocator, AutoLocator
# import matplotlib.dates as mdates

def custom_kosten_print(formatted_geldbedrag):
    temp = "{:,}".format(formatted_geldbedrag) #.replace(',','.')
    temp2 = format(temp).replace('.','#')
    temp3 = format(temp2).replace(',','.')
    temp4 = format(temp3).replace('#',',')
    return temp4

# Page settings
# st.set_page_config(layout="wide")


st.title("DUO Studieschuld Tool")

# Introduction
st.write("Met deze tool bereken je snel wat je maandelijkse aflosbedrag is als je binnen x-aantal jaar je studieschuld afbetaald wilt hebben.")
st.write("Óf bereken wanneer je studieschuld is afbetaald met een (hoger) gekozen maandelijks bedrag.")

# Tabs layout
tab1, tab2 = st.tabs(["Maandbedrag berekenen", "Aflosdatum berekenen"])

with tab1:
    st.write("You are in Tab 1")

with tab2:
    st.write("You are in Tab 2")

# st.header("This is a header")
# st.markdown("This is **Markdown**")
# st.caption("This is a figure caption")

# Input data collection
st.subheader("Studieschuld gegevens")

vandaag = datetime.date.today()
freq = pd.DateOffset(months=1)
max_bereik = pd.date_range(start=vandaag, periods=24+1, freq=freq)
max_begin_datum = max_bereik[-1]

# TODO: Session-state form

form_values = {
    "huidig_schuld_saldo": None,
    "jaarlijks_rente_percentage": None,
    "terugbetalen_in_jaren": None,
    "start_terugbetaling": None
}
with st.form(key="studieschuld_gegevens_form"):
    form_values["huidig_schuld_saldo"] = st.number_input(label="Hoogte studieschuld déze maand:",
                                          step=0.01,
                                          format="%0.2f",
                                          value=10000.00 # personal default: 30463.35 
                                          )
    
    form_values["jaarlijks_rente_percentage"] = st.number_input(label="Rente percentage (\u0025):", 
                                                 step=0.01,
                                                 format="%0.2f",
                                                 value=2.57
                                                 )/100

    form_values["terugbetalen_in_jaren"] = st.number_input(label="Terugbetalen in X jaar:",
                                            max_value=35,
                                            step=1,
                                            value=10
                                            )
    

    form_values["start_terugbetaling"] = st.date_input(label="Startdatum terugbetalingen:",
                                        max_value=max_begin_datum)

    submit_button = st.form_submit_button(label="Bevestig invoer")
    if submit_button:
        if not all(form_values.values()):
            st.warning("Vul alsjeblieft alle velden in om verder te gaan.")
        else:
            #st.balloons()
            st.success("Gegevens succesvol ingevoerd.")

print(form_values)

maandelijks_rente_percentage = (form_values["jaarlijks_rente_percentage"]  / 12)
print("Maandelijkse rente:", maandelijks_rente_percentage)

## Berekening sectie -- Terugbetaling in x jaar

aantal_maanden = (form_values["terugbetalen_in_jaren"] * 12)
data_terugbetalings_bereik = pd.date_range(start=form_values["start_terugbetaling"], periods=aantal_maanden+1, freq=freq)

# BRON Formule: https://www.investopedia.com/terms/a/amortization.asp
# Met maandelijks compound
maandbedrag = form_values["huidig_schuld_saldo"] * ((maandelijks_rente_percentage * (1 + maandelijks_rente_percentage)**aantal_maanden) / (((1 + maandelijks_rente_percentage)**aantal_maanden)-1))
print("Aflossingsbedrag per maand:", round(maandbedrag,2))
st.metric(label="Aflossingsbedrag per maand:", value=f"\u20ac {custom_kosten_print(round(maandbedrag,2))}")

# Bron formule: https://www.quora.com/What-is-the-correct-formula-for-how-long-until-balance-0-with-compound-interest-and-withdrawals-withdrawal-compound-interest-money
# maandbedrag_2 = huidig_schuld_saldo * (maandelijks_rente_percentage / (1-(1+maandelijks_rente_percentage)**(-aantal_maanden)))
# print(maandbedrag_2)

begin_rente = (form_values["huidig_schuld_saldo"] * maandelijks_rente_percentage)
print(f"Beginwaarde rente: {begin_rente}")

## Berekening Totaal Aflossingsschema Lening

resterend_schuld_saldo = form_values["huidig_schuld_saldo"]
print(f"Beginwaarde schuld: {resterend_schuld_saldo}")

toekomstige_schuld_saldos = []
toekomstige_schuld_saldos.append(form_values["huidig_schuld_saldo"])

toekomstige_rentes = []
toekomstige_rentes.append(0)

while resterend_schuld_saldo > 0.01:
    rente = (resterend_schuld_saldo * maandelijks_rente_percentage)

    resterend_schuld_saldo -= maandbedrag - rente
    
    toekomstige_schuld_saldos.append(round(resterend_schuld_saldo,2))
    toekomstige_rentes.append(round(rente,2))


s_schuld_saldos = pd.Series(toekomstige_schuld_saldos, index=data_terugbetalings_bereik, name="Toekomstige schuld saldos")
print(s_schuld_saldos)

s_rentes = pd.Series(toekomstige_rentes, index=data_terugbetalings_bereik, name="Toekomstige rentes")
print(s_rentes)

totale_rente_kosten = sum(toekomstige_rentes)

print("Totale kosten kwijt aan alleen rente:", custom_kosten_print(totale_rente_kosten))
st.metric(label="Totale kosten kwijt aan alléén rente:", value=f"\u20ac {custom_kosten_print(totale_rente_kosten)}")

totale_studieschuld = totale_rente_kosten + form_values["huidig_schuld_saldo"]
print("Studieschuld + totale rente:", round(totale_studieschuld,2))
st.metric(label="Studieschuld + totale rente:", value=f"\u20ac {custom_kosten_print(totale_studieschuld)}")

data_df = pd.concat([s_schuld_saldos, s_rentes], axis=1)
data_df["Cumulatieve rente"] = data_df["Toekomstige rentes"].cumsum()
data_df["Pure schuld afgelost"] = data_df["Toekomstige schuld saldos"].shift(1) - data_df["Toekomstige schuld saldos"]
data_df["Pure schuld afgelost"] = data_df["Pure schuld afgelost"].cumsum()

# Vervang de eerste waarde (nan) in de kolom "Pure schuld afgelost" met 0
data_df.iloc[0, 3] = 0
data_df.iloc[0, 1] = np.nan

print(data_df)

## Line Chart section
df_data_1 = data_df.loc[:, ["Toekomstige schuld saldos", "Toekomstige rentes"]]
# print(df_data_1)

st.subheader("Grafiek schuld verloop")
st.line_chart(data_df.loc[:, ["Toekomstige schuld saldos", "Pure schuld afgelost", "Cumulatieve rente"]])

st.subheader("Verloop maandelijkse rente")
st.line_chart(data_df.loc[:, ["Toekomstige rentes"]])




