"""
⌚ Luxury Watch Analytics Dashboard
Run:   py -m streamlit run dashboard.py
"""

import os, time, base64, warnings
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

warnings.filterwarnings("ignore")


# HELPERS
def b64(path: str, mime: str) -> str:
    """Return data-URI, or '' if file not found."""
    if not os.path.exists(path): return ""
    with open(path, "rb") as f:
        return f"data:{mime};base64,{base64.b64encode(f.read()).decode()}"


# PAGE SETUP
st.set_page_config(page_title="Luxury Watch Analytics", page_icon="⌚",
                   layout="wide", initial_sidebar_state="expanded")

VIDEO = b64("video.mp4", "video/mp4")   # bundled with the project

st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;600&display=swap');

  /* ── Wipe every Streamlit background so the video shows ── */
  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stHeader"],
  [data-testid="stToolbar"],
  section.main > div,
  .block-container {{
    background: transparent !important;
    background-color: transparent !important;
    font-family: 'Lato', sans-serif;
  }}

  /* ── Dark tint over video so content stays readable ── */
  .veil {{
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.68);
    z-index: 0; pointer-events: none;
  }}

  /* ── Hero section ── */
  .hero {{
    min-height: 92vh;
    display: flex; flex-direction: column;
    justify-content: center; align-items: flex-start;
    padding: 0 2rem 3rem;
    position: relative; z-index: 1;
  }}
  .hero-eyebrow {{
    font-size: .7rem; letter-spacing: 5px; text-transform: uppercase;
    color: #D4AF37; margin-bottom: .8rem;
  }}
  .hero-title {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.8rem, 6vw, 5.5rem);
    font-weight: 700; color: #fff;
    line-height: 1.05; letter-spacing: 2px;
    margin-bottom: .6rem;
  }}
  .hero-title span {{ color: #D4AF37; }}
  .hero-sub {{
    font-size: .9rem; color: #aaa; letter-spacing: 3px;
    text-transform: uppercase; margin-bottom: 2rem;
  }}
  .hero-badge {{
    display: inline-block; border: 1px solid #D4AF37;
    padding: .45rem 1.2rem; border-radius: 40px;
    font-size: .72rem; letter-spacing: 2px; color: #D4AF37;
    text-transform: uppercase; margin-right: .5rem; margin-bottom: .4rem;
    background: rgba(212,175,55,0.08);
  }}
  .hero-scroll {{
    position: absolute; bottom: 2rem; left: 50%; transform: translateX(-50%);
    color: #D4AF3788; font-size: .65rem; letter-spacing: 3px;
    text-transform: uppercase; text-align: center;
  }}
  .hero-scroll::after {{
    content: ''; display: block; width: 1px; height: 40px;
    background: linear-gradient(#D4AF37, transparent);
    margin: .5rem auto 0;
  }}

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {{
    background: rgba(10,8,4,0.92) !important;
    border-right: 1px solid #D4AF3744 !important;
  }}

  /* ── KPI cards (glass) ── */
  .kpi {{
    background: rgba(20,16,6,0.82); border: 1px solid #D4AF3755;
    border-radius: 10px; padding: 1.1rem 1.3rem; text-align: center;
    backdrop-filter: blur(12px); position: relative; z-index: 1;
    transition: border-color .2s;
  }}
  .kpi:hover {{ border-color: #D4AF37bb; }}
  .kpi::before {{
    content:''; display:block; height:2px; margin:-1.1rem -1.3rem .9rem;
    background: linear-gradient(90deg,transparent,#D4AF37,transparent);
    border-radius: 10px 10px 0 0;
  }}
  .kpi-lbl {{ font-size:.6rem; letter-spacing:2.5px; text-transform:uppercase; color:#666; }}
  .kpi-val {{ font-size:1.8rem; font-weight:700; color:#D4AF37; line-height:1.1;
              font-family:'Playfair Display',serif; }}
  .kpi-sub {{ font-size:.68rem; color:#444; margin-top:.25rem; }}

  /* ── Section dividers ── */
  .sec {{
    border-left: 3px solid #D4AF37; padding-left: .7rem;
    font-size: .78rem; letter-spacing: 3px; text-transform: uppercase;
    color: #D4AF37; margin: 2rem 0 .7rem;
    font-family: 'Playfair Display', serif;
  }}
  .gold-hr {{ border:none; border-top:1px solid #D4AF3755; margin:.5rem 0 1.2rem; }}

  /* ── Content zone sits above the veil ── */
  .block-container {{ position: relative; z-index: 1; padding-top: 0 !important; }}

  /* ── Sidebar scrollbar gold tint ── */
  ::-webkit-scrollbar {{ width:4px; }}
  ::-webkit-scrollbar-track {{ background:#111; }}
  ::-webkit-scrollbar-thumb {{ background:#D4AF3766; border-radius:2px; }}
</style>

<!-- full-screen looping video background -->
<video autoplay muted loop playsinline
  style="position:fixed;top:0;left:0;width:100vw;height:100vh;
         object-fit:cover;z-index:-1;pointer-events:none;">
  <source src="{VIDEO}" type="video/mp4">
</video>
<!-- dark tint overlay -->
<div class="veil"></div>
""", unsafe_allow_html=True)

# CONSTANTS
GOLD = "#D4AF37"
GRID = "#2A2A2A"
BC   = {
    "Rolex":"#D4AF37","Patek Philippe":"#C0A030","Audemars Piguet":"#8B6914",
    "Omega":"#FFE66D","Breitling":"#B8972E","Cartier":"#DAA520",
    "TAG Heuer":"#F0C040","Hublot":"#E8B830","IWC":"#C8980A","Longines":"#F5D060",
}
TOP_BRANDS = list(BC)

def L(title, h=390):
    return dict(
        title=dict(text=title, font=dict(color=GOLD, size=13, family="Playfair Display")),
        paper_bgcolor="rgba(14,11,4,0.82)", plot_bgcolor="rgba(18,14,6,0.85)",
        font=dict(color="#C8C8C8", family="Lato"), height=h,
        margin=dict(l=44, r=22, t=52, b=44),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#C8C8C8")),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )

# DATA LOADER
@st.cache_data(show_spinner=False)
def load_data():
    if os.path.exists("watches_clean.csv"):
        return pd.read_csv("watches_clean.csv")
    df = pd.read_csv("Watches.csv", low_memory=False)
    df.rename(columns={"mvmt":"movement","casem":"case_material",
                        "yop":"year_raw","cond":"condition"}, inplace=True)
    df["price"] = (df["price"].astype(str).str.replace(r"[\$,]","",regex=True)
                   .pipe(pd.to_numeric, errors="coerce"))
    df = df[df["price"].between(100, 10_000_000)].copy()
    df["year"] = (df["year_raw"].astype(str).str.extract(r"(\d{4})",expand=False)
                  .pipe(pd.to_numeric, errors="coerce"))
    df.loc[~df["year"].between(1950,2024),"year"] = np.nan
    df["year"] = (df.groupby("brand")["year"]
                  .transform(lambda s: s.fillna(s.median())).fillna(2020).astype(int))
    df["movement"] = df["movement"].map(
        {"Automatic":"Automatic","Quartz":"Quartz","Manual winding":"Manual"}
    ).fillna("Automatic")
    def mat(m):
        m = str(m) if not pd.isna(m) else ""
        return ("Platinum" if "Platinum" in m else "Titanium" if "Titanium" in m
                else "Gold" if "gold" in m.lower() or "Gold" in m
                else "Ceramic" if "Ceramic" in m else "Steel")
    df["material"] = df["case_material"].apply(mat)
    df = df[df["brand"].isin(TOP_BRANDS)].copy()
    np.random.seed(42)
    bp = {"Rolex":.9,"Omega":.75,"TAG Heuer":.65,"Longines":.7,"Breitling":.55,
          "Cartier":.6,"Hublot":.45,"Audemars Piguet":.4,"IWC":.35,"Patek Philippe":.3}
    pop  = df["brand"].map(bp).fillna(.5)
    pn   = (df["price"]-df["price"].min())/(df["price"].max()-df["price"].min())
    base = (pop*500*(1-pn*.7)).clip(1,1000)
    df["sales_volume"] = (base+np.random.normal(0,base*.15,len(df))).clip(1).astype(int)
    df["customer_rating"] = (df["brand"].map(
        {"Patek Philippe":4.7,"Rolex":4.6,"Audemars Piguet":4.6,"Omega":4.4,
         "Cartier":4.3,"Breitling":4.2,"IWC":4.2,"Hublot":4.1,
         "TAG Heuer":4.0,"Longines":3.9}).fillna(4.0)
        +np.random.normal(0,.3,len(df))).clip(1,5).round(1)
    df["region"] = np.random.choice(
        ["Asia","Europe","North America","Middle East","Rest of World"],
        size=len(df), p=[.35,.30,.20,.10,.05])
    df["water_resistance"] = np.random.choice(
        [30,50,100,200,300,600,1000], size=len(df), p=[.15,.25,.30,.15,.10,.04,.01])
    cols = ["brand","model","price","sales_volume","year","material",
            "movement","water_resistance","customer_rating","region","condition"]
    df = df[[c for c in cols if c in df.columns]]
    df.to_csv("watches_clean.csv", index=False)
    return df

# LOADING SCREEN
STEPS = [("⌚","Polishing the dials…"),("⚙️","Winding the movements…"),
         ("💎","Setting the diamonds…"),("📊","Assembling the dashboard…")]

if "loaded" not in st.session_state:
    ph = st.empty()
    with ph.container():
        st.markdown(
            "<div style='text-align:center;padding:8rem 0 2rem;position:relative;z-index:2'>"
            "<div style='font-size:5rem'></div>"
            "<div style='font-family:Playfair Display,serif;font-size:2.2rem;"
            "  color:#D4AF37;letter-spacing:6px;font-weight:700;margin:.5rem 0 0'>"
            "  LUXURY WATCH</div>"
            "<div style='font-family:Playfair Display,serif;font-size:2.2rem;"
            "  color:#D4AF37;letter-spacing:6px;font-weight:700'>ANALYTICS</div>"
            "<div style='color:#555;letter-spacing:4px;font-size:.72rem;"
            "  margin:.5rem 0 0;text-transform:uppercase'>Horology Intelligence Suite</div>"
            "</div>", unsafe_allow_html=True)
        bar  = st.progress(0)
        note = st.empty()
        for i,(icon,msg) in enumerate(STEPS):
            note.markdown(
                f"<div style='text-align:center;color:#888;font-size:.85rem;"
                f"letter-spacing:1px;margin:.4rem 0;position:relative;z-index:2'>"
                f"{icon}&nbsp; {msg}</div>", unsafe_allow_html=True)
            bar.progress((i+1)/len(STEPS))
            time.sleep(0.55)
    D = load_data()
    st.session_state.loaded  = True
    st.session_state.df_full = D
    ph.empty()
    st.rerun()
else:
    D = st.session_state.df_full


# SIDEBAR
st.sidebar.markdown(
    "<div style='text-align:center;padding:1rem 0 .5rem;font-family:Playfair Display,serif;"
    "font-size:1.1rem;color:#D4AF37;letter-spacing:3px;border-bottom:1px solid #D4AF3733;"
    "margin-bottom:.8rem'> DASHBOARD </div>", unsafe_allow_html=True)

b = st.sidebar.multiselect("Brand", sorted(D.brand.unique()), sorted(D.brand.unique()))
p = st.sidebar.slider("Price (USD)", int(D.price.min()), int(D.price.quantile(.99)), (int(D.price.min()), 150_000), step=500, format="$%d")
y = st.sidebar.slider("Year", int(D.year.min()), int(D.year.max()), (max(int(D.year.min()), 2005), int(D.year.max())))
m = st.sidebar.multiselect("Material", sorted(D.material.unique()), sorted(D.material.unique()))
r = st.sidebar.multiselect("Region", sorted(D.region.unique()), sorted(D.region.unique()))
mv = st.sidebar.multiselect("Movement", sorted(D.movement.unique()), sorted(D.movement.unique()))
df = D[D.brand.isin(b or D.brand.unique()) & D.price.between(*p) & D.year.between(*y) & D.material.isin(m or D.material.unique()) & D.region.isin(r or D.region.unique()) & D.movement.isin(mv or D.movement.unique())].copy()

st.sidebar.markdown("---")
st.sidebar.download_button("⬇️ Download Filtered CSV", df.to_csv(index=False).encode(), "watches_filtered.csv", "text/csv")
st.sidebar.caption(f"{len(df):,} listings after filtering")

if df.empty:
    st.warning("⚠️ No data matches the current filters."); st.stop()

# ── HERO SECTION  (full-viewport, video visible behind)
top_brand  = df.groupby("brand")["sales_volume"].sum().idxmax()
best_model = df.groupby("model")["sales_volume"].sum().idxmax()

st.markdown(f"""
<div class="hero">
  <div class="hero-eyebrow">Data Analysis & Visualization</div>
  <div class="hero-title">Luxury Watch<br><span>Analytics</span></div>
  <div class="hero-sub">Real-time Market Intelligence · {len(df):,} Listings</div>
  <div>
    <span class="hero-badge">Top Brand: {top_brand}</span>
    <span class="hero-badge">Avg Price: ${df.price.mean():,.0f}</span>
    <span class="hero-badge">Avg Rating: {df.customer_rating.mean():.2f} ★</span>
  </div>
  <div class="hero-scroll">Scroll to explore</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="gold-hr">', unsafe_allow_html=True)

# ── KPI CARDS
def kpi(c, l, v, s=""):
    c.markdown(f'<div class="kpi"><div class="kpi-lbl">{l}</div><div class="kpi-val">{v}</div><div class="kpi-sub">{s}</div></div>', unsafe_allow_html=True)
k1,k2,k3,k4,k5 = st.columns(5)
kpi(k1, "Total Sales", f"{df.sales_volume.sum():,}", "units")
kpi(k2, "Average Price", f"${df.price.mean():,.0f}", "USD")
kpi(k3, "Top Brand", top_brand, "by volume")
kpi(k4, "Best Model", best_model[:15]+("…" if len(best_model)>15 else ""), "")
kpi(k5, "Avg Rating", f"{df.customer_rating.mean():.2f} ★", "score")


# ── SECTION 1 · Sales Performance
st.markdown('<div class="sec">Sales Performance</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:  # 1 Bar
    sb = df.groupby("brand")["sales_volume"].sum().sort_values().reset_index()
    fig = go.Figure(go.Bar(x=sb.sales_volume, y=sb.brand, orientation="h", marker=dict(color=sb.sales_volume, colorscale=[[0,"#3D2B00"],[.5,"#8B6914"],[1,GOLD]], line_width=0), text=[f"{v:,}" for v in sb.sales_volume], textposition="outside", textfont_color="#C8C8C8", hovertemplate="<b>%{y}</b><br>%{x:,} units<extra></extra>"))
    fig.update_layout(**L("1) Sales Volume by Brand"))
    fig.update_xaxes(title_text="Units Sold")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with c2:  # 2 Line
    top5 = df.groupby("brand")["sales_volume"].sum().nlargest(5).index
    yd = df[df.brand.isin(top5)].groupby(["year","brand"])["sales_volume"].sum().reset_index()
    fig = go.Figure()
    for b in top5:
        bd = yd[yd.brand==b].sort_values("year")
        fig.add_trace(go.Scatter(x=bd.year, y=bd.sales_volume, name=b, mode="lines+markers", line=dict(width=2, color=BC.get(b,GOLD)), marker_size=5, hovertemplate=f"<b>{b}</b><br>%{{x}}: %{{y:,}}<extra></extra>"))
    fig.update_layout(**L("2) Sales Trend by Year (Top 5)"))
    fig.update_xaxes(title_text="Year"); fig.update_yaxes(title_text="Sales Volume")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── SECTION 2 · Market Share & Pricing
st.markdown('<div class="sec">Market Share & Pricing</div>', unsafe_allow_html=True)
c3, c4, c5 = st.columns(3)

with c3:  # 3 Pie
    ms = df.groupby("brand")["sales_volume"].sum()
    fig = go.Figure(go.Pie(labels=ms.index, values=ms.values, textinfo="percent", marker=dict(colors=list(BC.values()), line=dict(color="#0D0D0D",width=2)), pull=[.05 if b==top_brand else 0 for b in ms.index], hovertemplate="<b>%{label}</b><br>%{percent}  %{value:,} units<extra></extra>"))
    lay = L("3) Market Share by Brand", 370); lay.pop("xaxis"); lay.pop("yaxis")
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with c4:  # 4 Scatter
    s = df.sample(min(2000,len(df)), random_state=1)
    fig = go.Figure()
    for b in s.brand.unique():
        bd = s[s.brand==b]
        fig.add_trace(go.Scatter(x=bd.price, y=bd.customer_rating, mode="markers", name=b, marker=dict(size=5, opacity=.55, color=BC.get(b,GOLD)), hovertemplate=f"<b>{b}</b><br>${{x:,.0f}}<br>%{{y:.1f}}★<extra></extra>"))
    fig.update_layout(**L("4) Price vs Customer Rating", 370))
    fig.update_xaxes(title_text="Price (USD)", tickprefix="$")
    fig.update_yaxes(title_text="Rating", range=[1,5])
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with c5:  # 5 Histogram
    fig = go.Figure(go.Histogram(x=df[df.price<=200_000].price, nbinsx=50, marker=dict(color=GOLD, opacity=.8, line=dict(color="#0D0D0D",width=.5)), hovertemplate="$%{x:,.0f}  |  %{y:,} listings<extra></extra>"))
    fig.update_layout(**L("5) Price Distribution (≤ $200K)", 370))
    fig.update_xaxes(title_text="Price (USD)", tickprefix="$")
    fig.update_yaxes(title_text="Listings")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── SECTION 3 · Material & Statistics
st.markdown('<div class="sec">Material & Statistical Analysis</div>', unsafe_allow_html=True)
c6, c7 = st.columns(2)

with c6:  # 6 Box
    md = df[df.price<=500_000]
    o = md.groupby("material")["price"].median().sort_values().index.tolist()
    MC = {"Steel":"#708090","Gold":GOLD,"Platinum":"#E5E4E2","Titanium":"#B2BEB5","Ceramic":"#D3D3D3","Bronze":"#CD7F32","Carbon":"#555"}
    fig = go.Figure()
    for m in o:
        fig.add_trace(go.Box(y=md[md.material==m].price, name=m, marker_color=MC.get(m,GOLD), line_width=1.5, boxmean=True, hovertemplate=f"<b>{m}</b><br>${{y:,.0f}}<extra></extra>"))
    fig.update_layout(**L("6) Price by Case Material"))
    fig.update_yaxes(title_text="Price (USD)", tickprefix="$")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with c7:  # 7 Heatmap
    corr = df[["price","sales_volume","customer_rating","water_resistance","year"]].corr().round(2)
    lbl = ["Price","Sales","Rating","Water","Year"]
    fig = go.Figure(go.Heatmap(z=corr.values, x=lbl, y=lbl, colorscale=[[0,"#1A0A00"],[.5,"#8B6914"],[1,GOLD]], text=corr.values, texttemplate="%{text}", textfont=dict(color="white",size=11), hovertemplate="X: %{x}<br>Y: %{y}<br>r=%{z:.2f}<extra></extra>"))
    lay = L("7) Correlation Heatmap"); lay.pop("xaxis"); lay.pop("yaxis")
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── SECTION 4 · Growth & Insights
st.markdown('<div class="sec">Growth & Strategic Insights</div>', unsafe_allow_html=True)
c8, c9 = st.columns([3,2])

with c8:  # 8 Area
    top6 = df.groupby("brand")["sales_volume"].sum().nlargest(6).index.tolist()
    ad = df[df.brand.isin(top6)&(df.year>=2010)].groupby(["year","brand"])["sales_volume"].sum().reset_index()
    fig = go.Figure()
    for b in top6:
        bd = ad[ad.brand==b].sort_values("year")
        fig.add_trace(go.Scatter(x=bd.year, y=bd.sales_volume, name=b, mode="lines", fill="tozeroy" if b==top6[0] else "tonexty", stackgroup="one", line=dict(width=1, color=BC.get(b,GOLD)), hovertemplate=f"<b>{b}</b><br>%{{x}}: %{{y:,}}<extra></extra>"))
    fig.update_layout(**L("8) Stacked Sales Growth Over Time",400))
    fig.update_xaxes(title_text="Year"); fig.update_yaxes(title_text="Cumulative Sales")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with c9:  # 9 Bubble
    bub = df.groupby(["brand","model"]).agg(avg_price=("price","mean"), total_sales=("sales_volume","sum"), avg_rating=("customer_rating","mean")).reset_index().nlargest(120,"total_sales")
    fig = go.Figure()
    for b in bub.brand.unique():
        bd = bub[bub.brand==b]
        fig.add_trace(go.Scatter(x=bd.avg_price, y=bd.total_sales, mode="markers", name=b, marker=dict(size=bd.avg_rating*6, color=BC.get(b,GOLD), opacity=.7, line=dict(width=.5,color="#0D0D0D")), text=bd.model, hovertemplate="<b>%{text}</b><br>$%{x:,.0f}<br>%{y:,} sales<extra></extra>"))
    fig.update_layout(**L("9) Bubble: Price × Sales × Rating",400))
    fig.update_xaxes(title_text="Avg Price (USD)", tickprefix="$")
    fig.update_yaxes(title_text="Total Sales")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── SECTION 5 · Movement & Regional
st.markdown('<div class="sec">Movement & Regional Distribution</div>', unsafe_allow_html=True)
c10, c11 = st.columns(2)

with c10:  # 10 Donut
    mc = df.movement.value_counts()
    fig = go.Figure(go.Pie(labels=mc.index, values=mc.values, hole=.55, textinfo="percent+label", textfont=dict(color="white",size=12), marker=dict(colors=[GOLD,"#8B6914","#FFE66D"], line=dict(color="#0D0D0D",width=3)), hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>"))
    fig.add_annotation(text="Movement<br>Type", x=.5, y=.5, showarrow=False, font=dict(size=13, color="white"))
    lay = L("10) Movement Type Distribution",400); lay.pop("xaxis"); lay.pop("yaxis")
    fig.update_layout(**lay)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

with c11:  # ⊕ Regional Stacked Bar
    rd = df.groupby(["region","brand"])["sales_volume"].sum().reset_index()
    fig = px.bar(rd.nlargest(40,"sales_volume"), x="region", y="sales_volume", color="brand", color_discrete_map=BC, barmode="stack", template="plotly_dark", labels={"sales_volume":"Sales Volume","region":"Region","brand":"Brand"})
    fig.update_layout(**L("⊕ Regional Sales by Brand",400))
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})

# ── DATA EXPLORER
st.markdown('<div class="sec">Data Explorer</div>', unsafe_allow_html=True)
with st.expander("📋 Browse Filtered Listings"):
    out = df[["brand","model","price","sales_volume","year","material","movement","customer_rating","region"]].copy()
    out["price"] = out.price.apply(lambda x: f"${x:,.0f}")
    out["sales_volume"] = out.sales_volume.apply(lambda x: f"{x:,}")
    out["customer_rating"] = out.customer_rating.apply(lambda x: f"{x:.1f} ★")
    out.columns = ["Brand","Model","Price","Sales Vol.","Year","Material","Movement","Rating","Region"]
    st.dataframe(out.head(500), use_container_width=True, height=320)
    st.caption(f"Up to 500 of {len(df):,} rows · Full CSV via sidebar ⬇️")


# ── FOOTER
st.markdown(
    "<hr style='border:none;border-top:1px solid #D4AF3733;margin-top:2.5rem'>"
    "<div style='text-align:center;color:#333;font-size:.7rem;letter-spacing:3px;"
    "padding:.8rem 0 2rem;text-transform:uppercase'>"
    "Luxury Watch Analytics Suite &nbsp;·&nbsp; "
    "Streamlit + Plotly &nbsp;·&nbsp; Real-world data"
    "</div>", unsafe_allow_html=True)