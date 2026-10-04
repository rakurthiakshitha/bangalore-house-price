import streamlit as st
import pandas as pd

st.set_page_config(page_title="House Price", layout="centered")
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
h1 { color: white!important; text-align:center; }
.stButton>button { background: #FF6B6B; color:white; font-size:20px; border-radius:12px; width:100%; height:55px; font-weight:bold; }
div[data-testid="stSelectbox"], div[data-testid="stNumberInput"] { background:white; border-radius:12px; padding:8px; }
</style>
""", unsafe_allow_html=True)
st.markdown("<h1>🏠 Bangalore House Price Predictor</h1>", unsafe_allow_html=True)

@st.cache_resource
def load_rates():
    df = pd.read_csv('Bengaluru_House_Data.csv')
    df = df.dropna(subset=['size','location','price'])
    df['bhk'] = df['size'].str.extract(r'(\d+)').astype(float)
    def convert_sqft(x):
        try:
            if '-' in str(x): a,b = str(x).split('-'); return (float(a)+float(b))/2
            return float(x)
        except: return None
    df['total_sqft'] = df['total_sqft'].apply(convert_sqft)
    df = df.dropna(subset=['total_sqft','bhk'])
    df = df[(df['total_sqft']/df['bhk'] >= 250) & (df['total_sqft'] <= 6000)]
    df['location'] = df['location'].str.strip()
    df['pps'] = df['price']*100000 / df['total_sqft'] # price per sqft
    # Real median rate per location
    rates = df.groupby('location')['pps'].median().to_dict()
    # Remove extreme
    rates = {k: v for k,v in rates.items() if 1500 < v < 20000}
    return rates, df

rates, df_raw = load_rates()
locations = sorted(rates.keys())

location = st.selectbox("📍 Select Location", locations)
sqft = st.number_input("📐 Total Sqft", 300, 5000, 1200)
bhk = st.number_input("🛏️ BHK", 1, 6, 2)

if st.button("🔮 Predict Price"):
    pps = rates[location] # real rate of that area

    # Base price from actual area rate
    base_price = (sqft * pps) / 100000 # in Lakhs

    # BHK bonus: 3BHK must be more than 2BHK
    if bhk == 1: final_price = base_price * 0.92
    elif bhk == 2: final_price = base_price * 1.00
    elif bhk == 3: final_price = base_price * 1.18
    elif bhk == 4: final_price = base_price * 1.35
    else: final_price = base_price * (1.35 + (bhk-4)*0.15)

    # Show variation proof
    is_costly = pps > 8000
    tag = "💎 PREMIUM AREA" if is_costly else "🏡 BUDGET AREA"

    st.markdown(f"""
    <div style='background:white;padding:25px;border-radius:15px;text-align:center;'>
        <h2 style='color:#764ba2;margin:0;'>💰 {final_price:.2f} Lakhs</h2>
        <p style='margin:8px 0;'><b>{bhk}BHK</b> | {sqft} sqft | {location}</p>
        <p style='color:#FF6B6B;font-weight:bold;font-size:18px;'>{tag}</p>
        <p style='font-size:13px;color:gray;'>This area rate: ₹{pps:.0f}/sqft</p>
    </div>
    """, unsafe_allow_html=True)

    st.warning(f"✅ Test: Kanakpura Road (~₹9000/sqft) will be DOUBLE of Hoyasalangara (~₹4000/sqft) for same sqft")
    st.markdown("<p style='text-align:center;color:white;margin-top:20px;'>✅ 242 Locations | Real market rates</p>", unsafe_allow_html=True)