import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from utils.load_data import load_all
from utils.auth import require_login

# BLOCK access if not logged in
require_login()

data = load_all()
wca_summary = data['wca_summary']

# -----------------------
# Dummy Data Loader
# -----------------------
@st.cache_data
def load_data():
    countries = pd.DataFrame({
        'country_id':[1,2,3,4,5,6],
        'name':['Benin','Guinea','Niger','Mauritania','Senegal','Togo'],
        'iso3':['BEN','GIN','NER','MRT','SEN','TGO'],
        'lat':[9.31,9.95,17.61,20.26,14.5,8.62],
        'lon':[2.32,-9.7,8.08,-10.46,-14.45,0.82],
        'region':['WCA']*6,
        'income_level':['Lower-middle','Low','Low','Lower-middle','Lower-middle','Low']
    })

    products = pd.DataFrame({
        'product_id':[1,2,3],
        'disease':['HIV','TB','Malaria'],
        'product_name':['RHZE (Rifampicin/Isoniazid/Pyrazinamide/Ethambutol)',
                        'TLD (Tenofovir/Lamivudine/Dolutegravir)',                    
                        'Artemether-Lumefantrine 20/120mg'
                        ]
    })

    procurements = pd.DataFrame({
        'procurement_id':[1,2,3,4,5,6,7],
        'country_id':[1,1,2,3,4,5,6],
        'product_id':[1,2,3,1,2,1,3],
        'po_date':pd.to_datetime(['2024-02-01','2024-03-10','2024-01-20','2024-03-05','2024-04-01','2024-01-15','2024-02-12']),
        'delivery_date':pd.to_datetime(['2024-04-15','2024-05-25','2024-05-10','2024-07-02','2024-07-20','2024-03-10','2024-06-01']),
        'payment_date':pd.to_datetime(['2024-06-30','2024-06-10','2024-07-05','2024-10-01','2024-09-05','2024-03-30','2024-07-25']),
        'quantity_ordered':[500000,100000,200000,600000,80000,700000,250000],
        'quantity_delivered':[495000,100000,195000,580000,79000,700000,240000],
        'unit_price_local':[0.36,0.29,0.16,0.40,0.31,0.33,0.18],
        'currency':['XOF','XOF','GNF','XOF','MRU','XOF','XOF'],
        'funding_source':['Gov','Gov','Gov','Mixed','Gov','Gov','Mixed']
    })

    benchmarks = pd.DataFrame({
        'product_id':[1,2,3],
        'wambo_price_usd':[0.34,0.28,0.15],
        'gdf_price_usd':[0.33,0.29,0.14]
    })

    budgets = pd.DataFrame({
        'country_id':[1,2,3,4,5,6],
        'year':[2024]*6,
        'allocated_htm_usd':[12_000_000,8_000_000,9_500_000,5_000_000,15_000_000,7_000_000],
        'disbursed_htm_usd':[10_500_000,6_000_000,9_100_000,4_200_000,14_700_000,6_100_000],
        'funding_source':['Gov','Gov','Mixed','Gov','Gov','Mixed']
    })
    return countries, products, procurements, benchmarks, budgets

countries, products, procurements, benchmarks, budgets = load_data()

# -----------------------
# KPI Computations
# -----------------------
df = procurements.merge(countries, on='country_id').merge(products, on='product_id').merge(benchmarks, on='product_id')

df['lead_time_days'] = (df['delivery_date'] - df['po_date']).dt.days
df['payment_delay_days'] = (df['payment_date'] - df['delivery_date']).dt.days
df['fulfillment_rate'] = df['quantity_delivered'] / df['quantity_ordered']
df['price_variance_pct'] = (df['unit_price_local'] / df['wambo_price_usd'] - 1) * 100

budgets['budget_execution_rate'] = budgets['disbursed_htm_usd'] / budgets['allocated_htm_usd']

kpis = df.groupby(['country_id','name','iso3','lat','lon']).agg({
    'lead_time_days':'mean',
    'payment_delay_days':'mean',
    'fulfillment_rate':'mean',
    'price_variance_pct':'mean'
}).reset_index().merge(budgets[['country_id','budget_execution_rate']], on='country_id')

# Simple normalized composite risk score
kpis['risk_score'] = (
    (kpis['lead_time_days']/kpis['lead_time_days'].max())*0.4 +
    (kpis['payment_delay_days']/kpis['payment_delay_days'].max())*0.3 +
    (kpis['price_variance_pct']/kpis['price_variance_pct'].max())*0.2 +
    ((1-kpis['fulfillment_rate'])/ (1-kpis['fulfillment_rate']).max())*0.1
)

# -----------------------
# Streamlit UI
# -----------------------
st.title("HTM Procurement & PFM")
st.caption("Dummy Data – 6 Francophone WCA Countries")

view = st.sidebar.radio("Select View", ["Regional Overview","Country Dashboard","Risk Simulation"])

# -----------------------
# REGIONAL OVERVIEW
# -----------------------
if view == "Regional Overview":
    st.subheader("Regional Overview")

   
    st.markdown("#### KPI Summary")
    st.dataframe(kpis[['name','lead_time_days','payment_delay_days',
                           'fulfillment_rate','price_variance_pct',
                           'budget_execution_rate','risk_score']].rename(columns={
                               'name':'Country',
                               'lead_time_days':'Lead Time (days)',
                               'payment_delay_days':'Payment Delay (days)',
                               'fulfillment_rate':'Fulfillment Rate',
                               'price_variance_pct':'Price Variance (%)',
                               'budget_execution_rate':'Budget Exec.',
                               'risk_score':'Risk Score'
                           }).style.format({
                               'Lead Time (days)':"{:.0f}",
                               'Payment Delay (days)':"{:.0f}",
                               'Fulfillment Rate':"{:.2%}",
                               'Price Variance (%)':"{:.1f}",
                               'Budget Exec.':"{:.2%}",
                               'Risk Score':"{:.2f}"
                           }))
   
    st.markdown("Regional Risk Map")
    fig_map = px.choropleth(
            kpis,
            locations='iso3',
            color='risk_score',
            hover_name='name',
            hover_data={
                'lead_time_days':':.0f',
                'payment_delay_days':':.0f',
                'fulfillment_rate':':.2%',
                'price_variance_pct':':.1f',
                'budget_execution_rate':':.2%',
                'risk_score':':.2f'
            },
            color_continuous_scale='Reds',
            range_color=(0, kpis['risk_score'].max()),
            title="Composite Risk Score by Country"
        )

        # Focus only on Africa
    fig_map.update_geos(
            visible=False,
            resolution=50,
            showcountries=True,
            countrycolor="lightgrey",
            scope="africa",
            projection_type="mercator",
            showland=True,
            landcolor="whitesmoke"
        )

    fig_map.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            geo=dict(bgcolor='rgba(0,0,0,0)'),
        )
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Display each sub-topic and summary
    st.title("Regional Summary")
    for idx, row in wca_summary.iterrows():
        st.markdown(f"### {row['Sub-Topic']}")
        st.markdown(f"{row['Regional Summary']}")


st.caption("© 2025 HTM Procurement Mapping – Regional Prototype (Dummy Data)")

# -----------------------
# COUNTRY DASHBOARD
# -----------------------
if view == "Country Dashboard":
    country = st.selectbox("Select Country", kpis['name'])
    data_c = df[df['name']==country]
    st.subheader(f"{country} – Procurement KPIs")

    ckpi = kpis[kpis['name']==country].iloc[0]
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("Lead Time (days)", f"{ckpi['lead_time_days']:.0f}")
    c2.metric("Payment Delay (days)", f"{ckpi['payment_delay_days']:.0f}")
    c3.metric("Fulfillment Rate", f"{ckpi['fulfillment_rate']:.0%}")
    c4.metric("Price Variance", f"{ckpi['price_variance_pct']:.1f}%")
    c5.metric("Budget Execution", f"{ckpi['budget_execution_rate']:.0%}")

    fig_a = px.bar(data_c, x='product_name', y='lead_time_days', color='funding_source', title="Lead Time by Product")
    st.plotly_chart(fig_a, use_container_width=True)

    fig_b = px.bar(data_c, x='product_name', y='fulfillment_rate', color='disease', title="Fulfillment Rate", text_auto=".0%")
    st.plotly_chart(fig_b, use_container_width=True)

    fig_c = px.bar(data_c, x='product_name', y='price_variance_pct', color='disease', title="Price Variance vs Benchmark (%)")
    st.plotly_chart(fig_c, use_container_width=True)

# -----------------------
# RISK SIMULATION
# -----------------------
if view == "Risk Simulation":
    st.subheader("Monte Carlo Risk Simulation (Dummy Model)")
    st.markdown("""
    This module estimates the probability of **delayed delivery** (>90 days lead time)
    and **stock-out risk** (fulfillment rate <95%) using 10,000 random draws from observed distributions.
    """)

    N = st.slider("Number of Simulations", 1000, 20000, 10000, 1000)
    np.random.seed(42)

    lead_mu, lead_sigma = df['lead_time_days'].mean(), df['lead_time_days'].std()
    fulfill_mu, fulfill_sigma = df['fulfillment_rate'].mean(), df['fulfillment_rate'].std()

    simulated_lead = np.random.normal(lead_mu, lead_sigma, N)
    simulated_fulfill = np.random.normal(fulfill_mu, fulfill_sigma, N)

    prob_delay = np.mean(simulated_lead > 90)
    prob_stockout = np.mean(simulated_fulfill < 0.95)

    c1,c2 = st.columns(2)
    c1.metric("P(Delay > 90 days)", f"{prob_delay*100:.1f}%")
    c2.metric("P(Stock-out <95%)", f"{prob_stockout*100:.1f}%")

    fig_sim1 = px.histogram(simulated_lead, nbins=40, title="Simulated Lead Time Distribution (days)")
    st.plotly_chart(fig_sim1, use_container_width=True)

    fig_sim2 = px.histogram(simulated_fulfill, nbins=40, title="Simulated Fulfillment Rate Distribution")
    st.plotly_chart(fig_sim2, use_container_width=True)



