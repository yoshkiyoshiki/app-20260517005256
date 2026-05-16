import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

st.set_page_config(page_title="CashLens", page_icon="💰", layout="wide")

st.markdown("""
<style>
.big-score { font-size: 72px; font-weight: bold; text-align: center; }
.grade-badge { font-size: 36px; font-weight: bold; text-align: center; padding: 10px; border-radius: 50%; }
.story-card { background: #1e1e2e; padding: 20px; border-radius: 12px; border-left: 4px solid #7c3aed; }
</style>
""", unsafe_allow_html=True)

COMPANIES = {
    "Apple (AAPL)": {"fcf_growth": 12, "fcf_margin": 28, "capex_ratio": 8, "debt_coverage": 85, "fcf_stability": 92},
    "Microsoft (MSFT)": {"fcf_growth": 15, "fcf_margin": 35, "capex_ratio": 10, "debt_coverage": 90, "fcf_stability": 95},
    "Toyota (7203)": {"fcf_growth": 5, "fcf_margin": 8, "capex_ratio": 22, "debt_coverage": 60, "fcf_stability": 70},
    "Sony (6758)": {"fcf_growth": 8, "fcf_margin": 10, "capex_ratio": 18, "debt_coverage": 65, "fcf_stability": 72},
    "Tesla (TSLA)": {"fcf_growth": 25, "fcf_margin": 12, "capex_ratio": 30, "debt_coverage": 55, "fcf_stability": 50},
}

def calc_cf_score(metrics):
    weights = {"fcf_growth": 0.25, "fcf_margin": 0.25, "capex_ratio": 0.15, "debt_coverage": 0.2, "fcf_stability": 0.15}
    score = (
        min(metrics["fcf_growth"] / 20 * 100, 100) * weights["fcf_growth"] +
        min(metrics["fcf_margin"] / 40 * 100, 100) * weights["fcf_margin"] +
        max((100 - metrics["capex_ratio"]) / 80 * 100, 0) * weights["capex_ratio"] +
        metrics["debt_coverage"] * weights["debt_coverage"] +
        metrics["fcf_stability"] * weights["fcf_stability"]
    )
    return round(score)

def score_to_grade(score):
    if score >= 85: return "A", "#22c55e"
    if score >= 70: return "B", "#84cc16"
    if score >= 55: return "C", "#eab308"
    if score >= 40: return "D", "#f97316"
    return "E", "#ef4444"

st.title("💰 CashLens（キャッシュレンズ）")
st.caption("キャッシュフローで見抜く、未来の資産を描く")

tabs = st.tabs(["📊 CFスコア分析", "📈 投資リターン試算", "💹 企業ランキング"])

with tabs[0]:
    st.subheader("CFスコア（キャッシュフロー健全性）")
    col1, col2 = st.columns([1, 2])
    with col1:
        selected = st.selectbox("企業を選択", list(COMPANIES.keys()))
    
    metrics = COMPANIES[selected]
    score = calc_cf_score(metrics)
    grade, color = score_to_grade(score)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "CFスコア"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": color},
                "steps": [
                    {"range": [0, 40], "color": "#fee2e2"},
                    {"range": [40, 60], "color": "#fef9c3"},
                    {"range": [60, 80], "color": "#dcfce7"},
                    {"range": [80, 100], "color": "#bbf7d0"},
                ],
                "threshold": {"line": {"color": "black", "width": 4}, "thickness": 0.75, "value": score}
            }
        ))
        fig_gauge.update_layout(height=250, margin=dict(t=30, b=0))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown(f"<div style='text-align:center; font-size:48px; color:{color}; font-weight:bold'>Grade {grade}</div>", unsafe_allow_html=True)

    with col_b:
        categories = ["FCF成長率", "FCFマージン", "設備投資比率", "負債カバー率", "FCF安定性"]
        values = [
            min(metrics["fcf_growth"] / 20 * 100, 100),
            min(metrics["fcf_margin"] / 40 * 100, 100),
            max((100 - metrics["capex_ratio"]) / 80 * 100, 0),
            metrics["debt_coverage"],
            metrics["fcf_stability"],
        ]
        fig_radar = go.Figure(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor=f"rgba(124,58,237,0.3)",
            line_color="#7c3aed",
            name=selected
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            height=300, margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_c:
        st.markdown("#### 指標詳細")
        df_metrics = pd.DataFrame({
            "指標": categories,
            "スコア": [f"{v:.0f}点" for v in values],
            "評価": ["✅" if v >= 70 else "⚠️" if v >= 50 else "❌" for v in values]
        })
        st.dataframe(df_metrics, hide_index=True, use_container_width=True)
        
        st.markdown("#### 💡 AIストーリー")
        fcf_est = metrics["fcf_margin"] * 10
        st.markdown(f"""<div class='story-card'>
        <b>{selected}</b>は毎年売上の<b>{metrics['fcf_margin']}%</b>に相当する
        フリーキャッシュフローを生み出しています。FCF成長率は年<b>{metrics['fcf_growth']}%</b>で推移しており、
        負債カバー率は<b>{metrics['debt_coverage']}点</b>と{'健全' if metrics['debt_coverage'] >= 70 else '要注意'}な水準です。
        </div>""", unsafe_allow_html=True)

with tabs[1]:
    st.subheader("📈 投資リターンシミュレーター")
    col1, col2 = st.columns([1, 2])

    with col1:
        invest_amount = st.