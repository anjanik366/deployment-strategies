import streamlit as st
import json
import sys
from pathlib import Path

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.models import (
    SystemRequirements,
    WorkloadType,
    BudgetTier,
    TrafficPattern,
    GPURequirement,
    AuthRequirement,
    ProtocolRequirement,
    StorageRequirement
)
from engine.decision_engine import DecisionEngine

st.set_page_config(
    page_title="Cloud Deployment Strategy Recommender",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧭 Cloud Deployment Strategy Decision Engine")
st.markdown(
    """
    Evaluate system architecture requirements against **AWS**, **Microsoft Azure**, and **Google Cloud Platform (GCP)**.
    Get personalized strategy recommendations, cost estimations, trade-off matrices, and copy-paste deployment CLI commands.
    """
)

# Sidebar: System Requirements Input
st.sidebar.header("⚙️ System Requirements")

app_name = st.sidebar.text_input("Application Name", value="My Cloud Service")

workload = st.sidebar.selectbox(
    "Workload Type",
    options=[e.value for e in WorkloadType],
    index=0,
    help="Select the core workload domain and runtime architecture."
)

budget = st.sidebar.selectbox(
    "Budget Tier / Cost Tolerance",
    options=[e.value for e in BudgetTier],
    index=1,
    help="Target monthly expenditure tolerance."
)

traffic = st.sidebar.selectbox(
    "Traffic Pattern",
    options=[e.value for e in TrafficPattern],
    index=0,
    help="Sporadic workloads benefit significantly from scale-to-zero."
)

gpu = st.sidebar.selectbox(
    "GPU Hardware Acceleration",
    options=[e.value for e in GPURequirement],
    index=0,
    help="Select if your app runs dedicated LLM, Whisper, or PyTorch inference."
)

auth = st.sidebar.selectbox(
    "Authentication / Identity Ecosystem",
    options=[e.value for e in AuthRequirement],
    index=0,
    help="Select Microsoft Entra ID if your app requires single sign-on with Azure AD."
)

protocol = st.sidebar.selectbox(
    "Protocol & Connection Lifetime",
    options=[e.value for e in ProtocolRequirement],
    index=1,
    help="Streamlit and real-time streaming require WebSocket support."
)

storage = st.sidebar.selectbox(
    "Storage Persistence",
    options=[e.value for e in StorageRequirement],
    index=0
)

cloud_bias = st.sidebar.selectbox(
    "Cloud Preference / Team Expertise",
    options=["any", "gcp", "aws", "azure"],
    index=0
)

# Build Pydantic model
reqs = SystemRequirements(
    app_name=app_name,
    workload_type=WorkloadType(workload),
    budget_tier=BudgetTier(budget),
    traffic_pattern=TrafficPattern(traffic),
    gpu_requirement=GPURequirement(gpu),
    auth_requirement=AuthRequirement(auth),
    protocol=ProtocolRequirement(protocol),
    storage=StorageRequirement(storage),
    team_cloud_familiarity=cloud_bias
)

engine = DecisionEngine()
result = engine.evaluate(reqs)
pri = result.primary_strategy
run = result.runner_up_strategy
alt = result.alternative_local_or_vps

# Layout Main Columns
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader(f"🏆 Primary Recommendation: {pri.service_name}")
    st.markdown(f"**Provider**: `{pri.cloud_provider}` | **Tier**: `{pri.architecture_tier}` | **Fit Score**: `{pri.fit_score}/100`")
    st.success(f"💰 **Estimated Monthly Cost:** {pri.estimated_monthly_cost}")
    
    st.markdown("#### 💡 Strategic Justification")
    st.write(pri.why_recommended)
    
    st.markdown("#### ✨ Key Advantages")
    for adv in pri.key_advantages:
        st.markdown(f"- {adv}")
        
    st.markdown("#### ⚠️ Trade-offs & Risks")
    for tro in pri.tradeoffs_and_risks:
        st.markdown(f"- {tro}")

    st.markdown("#### ⚡ Quickstart Deployment Command")
    st.code(pri.quickstart_cli_command, language="bash")

with col2:
    st.subheader(f"🥈 Runner-Up: {run.service_name}")
    st.markdown(f"**Provider**: `{run.cloud_provider}` | **Fit Score**: `{run.fit_score}/100`")
    st.info(f"💰 **Estimated Cost:** {run.estimated_monthly_cost}")
    st.caption(f"**Why runner-up:** {run.why_recommended}")
    st.markdown(f"**Documentation:** `{run.doc_reference}`")
    
    st.divider()
    
    if alt and alt.service_name != pri.service_name:
        st.subheader(f"🏡 Zero-Cost / Edge Option")
        st.markdown(f"**Option**: `{alt.service_name}`")
        st.markdown(f"**Cost**: `{alt.estimated_monthly_cost}`")
        st.caption(alt.key_advantages[0])
        st.code(alt.quickstart_cli_command, language="bash")

st.divider()

# Decision Rationale & Next Steps
st.subheader("📋 Decision Rationale & Pre-Flight Action Checklist")
st.write(result.architecture_decision_rationale)

checklist_col1, checklist_col2 = st.columns(2)
with checklist_col1:
    st.markdown("##### Deployment Checklist")
    for item in result.action_checklist:
        st.markdown(f"- [ ] {item}")

with checklist_col2:
    st.markdown("##### Quick Reference Links")
    st.markdown(f"- 📘 [AWS Implementation Guide](./AWS_Deployment.md)")
    st.markdown(f"- 🔷 [Azure Implementation Guide](./Azure_Deployment.md)")
    st.markdown(f"- 🇬 [GCP Implementation Guide](./GCP_Deployment.md)")
    st.markdown(f"- 📊 [Comprehensive Comparison & Benchmarks](./Conclusion.md)")
    st.markdown(f"- 📜 [System Architecture & Scoring Engine](./System_Architecture_and_Engine.md)")
    st.markdown(f"- 🛠️ [Step-by-Step Deployment Playbooks](./Step_by_Step_Deployment_Guide.md)")
