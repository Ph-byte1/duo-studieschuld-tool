# -*- coding: utf-8 -*-
"""
Created on Sat Jan 11 12:48:15 2025

@author: Phvan
"""
# %% Setup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter, MaxNLocator, FixedLocator, AutoLocator
import matplotlib.dates as mdates
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

huidig_schuld_saldo = 30463.35 
jaarlijks_rente_percentage = round((2.57 / 100),4)
terugbetalen_in_jaren = 10
start_terugbetaling = pd.Timestamp('2024-12-01')

print(jaarlijks_rente_percentage)

# %% Setup
maandelijks_rente_percentage = (jaarlijks_rente_percentage / 12)
print(maandelijks_rente_percentage)

aantal_maanden = (terugbetalen_in_jaren * 12)
freq = pd.DateOffset(months=1)

data_terugbetalings_bereik = pd.date_range(start=start_terugbetaling, periods=aantal_maanden+1, freq=freq)
data_terugbetalings_bereik

# %% Terugbetaling in x jaar

# BRON Formule: https://www.investopedia.com/terms/a/amortization.asp
# Met maandelijks compound
maandbedrag = huidig_schuld_saldo * ((maandelijks_rente_percentage * (1 + maandelijks_rente_percentage)**aantal_maanden) / (((1 + maandelijks_rente_percentage)**aantal_maanden)-1))
print("Aflossingsbedrag per maand:", round(maandbedrag,2))

# Bron formule: https://www.quora.com/What-is-the-correct-formula-for-how-long-until-balance-0-with-compound-interest-and-withdrawals-withdrawal-compound-interest-money
# maandbedrag_2 = huidig_schuld_saldo * (maandelijks_rente_percentage / (1-(1+maandelijks_rente_percentage)**(-aantal_maanden)))
# print(maandbedrag_2)

# %% Rente

begin_rente = (huidig_schuld_saldo * maandelijks_rente_percentage)
print(begin_rente)


# %% Totaal Aflossingsschema lening

resterend_schuld_saldo = huidig_schuld_saldo
print(f"Beginwaarde resterende schuld: {resterend_schuld_saldo}")

toekomstige_schuld_saldos = []
toekomstige_schuld_saldos.append(huidig_schuld_saldo)

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
print(toekomstige_rentes)

totale_rente_kosten = sum(toekomstige_rentes)
print("Totale kosten kwijt aan alleen rente:", totale_rente_kosten)

totale_studieschuld = totale_rente_kosten + huidig_schuld_saldo
print("Studieschuld + totale rente:", round(totale_studieschuld,2))

# %%
data_df = pd.concat([s_schuld_saldos, s_rentes], axis=1)
data_df["Cumulatieve rente"] = data_df["Toekomstige rentes"].cumsum()
data_df["Pure schuld afgelost"] = data_df["Toekomstige schuld saldos"].shift(1) - data_df["Toekomstige schuld saldos"]
data_df["Pure schuld afgelost"] = data_df["Pure schuld afgelost"].cumsum()

# Vervang de eerste waarde (nan) in de kolom "Pure schuld afgelost" met 0
data_df.iloc[0, 3] = 0
data_df.iloc[0, 1] = np.nan
data_df

# %% Plot
#-- Create figure and axis objects
fig, ax1 = plt.subplots(figsize=(14,6), dpi=400)

sns.set_style("darkgrid")
# sns.set_style("whitegrid")

#------------------------------------------------------------------------------
# ax1 
#------------------------------------------------------------------------------
#-- Lineplot
for col in data_df.columns[[0, 2, 3]]:
    print(col)

    sns.lineplot(data=data_df, x=data_df.index, y=data_df[col],
                  label=col,
                  ax=ax1,
                  legend=False
                  )

#-- January points
january_points = data_df[data_df.index.month == 1]
last_entry = data_df.tail(1)
january_points = pd.concat([january_points, last_entry])

for col in january_points.columns[[0, 2, 3]]:
    sns.scatterplot(data=january_points, x=january_points.index, y=col, 
                    ax=ax1, s=50,
                    legend=False
                    )
    
#-- ax1 settings
ax1.set_xlabel('Jaar', labelpad=10, fontsize=12, fontweight='bold')
ax1.set_ylabel('Geldbedrag in euro\'s', color='black', labelpad=10, fontsize=12, fontweight='bold')

ax1.tick_params(axis='y', labelcolor='black', left=True)
ax1.tick_params(axis='x', which='both', bottom=True, top=False)

# Format y-axis labels with thousand separators
ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}".replace(",", ".")))

ax1.xaxis.set_major_locator(mdates.YearLocator(base=2))

# Rotate x-axis ticks
plt.xticks(rotation=0)

#------------------------------------------------------------------------------
# ax2
#------------------------------------------------------------------------------
#-- instantiate a second axes that shares the same x-axis
ax2 = ax1.twinx()

#-- Lineplot
sns.lineplot(data=data_df, x=data_df.index, y=data_df["Toekomstige rentes"],
              label="Toekomstige rentes",
              ax=ax2,
              color='red',
              legend=False
              )

#-- January points for "Toekomstige rentes"
sns.scatterplot(data=january_points, x=january_points.index, y="Toekomstige rentes",
                ax=ax2, s=50, 
                color='red', 
                legend=False
                )

ax2.set_ylabel('Rente in euro\'s', color='black', labelpad=10, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor='black', right=True)


# l = ax1.get_ylim()
# l2 = ax2.get_ylim()
# f = lambda x : l2[0] + (x-l[0]) / (l[1]-l[0]) * (l2[1]-l2[0])
# ticks = f(ax1.get_yticks())
# ax2.yaxis.set_major_locator(FixedLocator(ticks))


ax2.yaxis.set_major_locator(MaxNLocator(nbins=8, 
                                        #integer=True,
                                        # symmetric=True
                                        ))

#-- Set same grid options for both axes
# ax1 = plt.gca()
ax1.grid(True, linestyle=':')
ax1.set_axisbelow(True)
ax2.grid(True, linestyle=':')
ax2.set_axisbelow(True)

#-- Add thicker outer border
for spine in ax2.spines.values():
    spine.set_color('black')
    spine.set_linewidth(0.5)
        
#-- Get the handles and labels of both y-axis legends
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()

# Combine handles and labels
all_handles = handles1 + handles2
all_labels = labels1 + labels2

#-- Plot the combined legend at the specified position
plt.legend(all_handles, all_labels,
           framealpha=1,
           facecolor='white',
           loc='center left', 
           fontsize=11,
           # bbox_to_anchor=(0.5, 0.5)
           )

plt.tight_layout()
plt.show()
plt.close(fig)

# %% Plotly plot

# Create a Plotly figure
fig = make_subplots(specs=[[{"secondary_y": True}]])
# fig = go.Figure()

# Add line plots for columns A, B, C
for col in data_df.columns[[0, 2, 3]]:
    fig.add_trace(
        go.Scatter(x=data_df.index, y=data_df[col], mode="lines", name=col),
        secondary_y=False,
    )

# Add scatter points for January and the last data entry
for col in data_df.columns[[0, 2, 3]]:
    fig.add_trace(
        go.Scatter(
            x=january_points.index,
            y=january_points[col],
            mode="markers",
        ),
        secondary_y=False,
    )

# Add line plot for column D
fig.add_trace(
    go.Scatter(x=data_df.index, y=data_df["Toekomstige rentes"], mode="lines", name="Toekomstige rentes", 
               # line=dict(color="orange")
               ),
    secondary_y=True,
)

# Add scatter points for column D (January and last data entry)
fig.add_trace(
    go.Scatter(
        x=january_points.index,
        y=january_points["Toekomstige rentes"],
        mode="markers",
        # marker=dict(color="orange"),
    ),
    secondary_y=True,
)

# Update layout for better readability
fig.update_layout(
    title="Interactive Plot with Multiple Y Axes",
    xaxis_title="Date",
    yaxis_title="Primary Axis (Values in Thousands)",
    legend_title="Legend",
)

# Update secondary y-axis
fig.update_yaxes(title_text="Secondary Axis", secondary_y=True)

# Set x-axis to show ticks every year and rotate labels
fig.update_xaxes(
    tickformat="%Y",  # Year format
    dtick="M12",  # One tick every 12 months
    tickangle=-45,  # Rotate labels
)

# Save the figure to an HTML file
html_file = "./interactive_plot.html"
pio.write_html(fig, file=html_file, auto_open=True)

# Optionally, open in the browser
#webbrowser.open(html_file)

# %%
# def verloop_studieschuld_in_x_jaar():
    
#     wettelijk_maandbedrag = None
    
#     return wettelijk_maandbedrag















