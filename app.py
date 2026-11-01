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
from engine.presets import PRESET_PROFILES

st.set_page_config(
    page_title="Cloud Deployment Strategy Decision Engine",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section
st.title("🧭 Cloud Deployment Strategy Decision Engine")
st.markdown(
    """
    Evaluate system architecture requirements across **AWS**, **Microsoft Azure**, and **Google Cloud Platform (GCP)**.
    Select a **pre-configured architecture scenario** or tune individual requirements below to get instant recommendations, 
    estimated monthly costs, trade-off matrices, and copy-paste CLI deployment commands.
    """
)

# Sidebar: Preset & Custom Requirement Selectors
st.sidebar.header("🎯 1. Architectural Presets")

preset_names = list(PRESET_PROFILES.keys())
selected_preset_name = st.sidebar.selectbox(
    "Choose a Pre-Configured Scenario:",
    options=preset_names,
    index=1,
    help="Select a common production scenario or choose 'Custom' to manually specify every parameter."
)

preset_info = PRESET_PROFILES[selected_preset_name]
st.sidebar.caption(f"ℹ️ {preset_info['description']}")

# Determine default values based on preset
defaults = preset_info["requirements"]

st.sidebar.divider()
st.sidebar.header("⚙️ 2. Custom Requirements")

app_name_default = defaults.app_name if defaults else "My Cloud Service"
app_name = st.sidebar.text_input("Application Name", value=app_name_default)

# Workload Type
workload_options = [e.value for e in WorkloadType]
workload_default_idx = workload_options.index(defaults.workload_type.value) if defaults else 0
workload = st.sidebar.selectbox(
    "Workload Type",
    options=workload_options,
    index=workload_default_idx,
    help="Core application runtime domain (Web UI, REST API, Dedicated GPU AI, Web Scraper, Microservices)."
)

# Budget Tier
budget_options = [e.value for e in BudgetTier]
budget_default_idx = budget_options.index(defaults.budget_tier.value) if defaults else 0
budget = st.sidebar.selectbox(
    "Budget Tier / Cost Tolerance",
    options=budget_options,
    index=budget_default_idx,
    help="Target monthly expenditure tolerance ($0 free tier, <$5 ultra low, flat predictable VPS, standard, enterprise)."
)

# Traffic Pattern
traffic_options = [e.value for e in TrafficPattern]
traffic_default_idx = traffic_options.index(defaults.traffic_pattern.value) if defaults else 0
traffic = st.sidebar.selectbox(
    "Traffic Pattern",
    options=traffic_options,
    index=traffic_default_idx,
    help="Sporadic/bursty usage requires fast scale-to-zero to avoid idle compute billing."
)

# GPU Acceleration
gpu_options = [e.value for e in GPURequirement]
gpu_default_idx = gpu_options.index(defaults.gpu_requirement.value) if defaults else 0
gpu = st.sidebar.selectbox(
    "GPU Hardware Acceleration",
    options=gpu_options,
    index=gpu_default_idx,
    help="Dedicated on-device GPU acceleration (e.g., Nvidia L4 24GB or Nvidia T4 16GB for LLMs/Whisper)."
)

# Auth Ecosystem
auth_options = [e.value for e in AuthRequirement]
auth_default_idx = auth_options.index(defaults.auth_requirement.value) if defaults else 0
auth = st.sidebar.selectbox(
    "Authentication / Identity Ecosystem",
    options=auth_options,
    index=auth_default_idx,
    help="Select Microsoft Entra ID if your app requires single sign-on with Azure AD."
)

# Protocol & WebSockets
protocol_options = [e.value for e in ProtocolRequirement]
protocol_default_idx = protocol_options.index(defaults.protocol.value) if defaults else 1
protocol = st.sidebar.selectbox(
    "Protocol & Connection Lifetime",
    options=protocol_options,
    index=protocol_default_idx,
    help="Streamlit and real-time streaming require persistent WebSocket support with >300s timeouts."
)

# Storage Persistence
storage_options = [e.value for e in StorageRequirement]
storage_default_idx = storage_options.index(defaults.storage.value) if defaults else 0
storage = st.sidebar.selectbox(
    "Storage Persistence",
    options=storage_options,
    index=storage_default_idx,
    help="Stateless ephemeral storage, mounted file volume (SMB / FUSE / NFS), or managed DB."
)

# Cloud Bias
cloud_bias_options = ["any", "gcp", "aws", "azure"]
bias_default = defaults.team_cloud_familiarity if defaults and defaults.team_cloud_familiarity in cloud_bias_options else "any"
cloud_bias = st.sidebar.selectbox(
    "Cloud Provider Preference / Team Expertise",
    options=cloud_bias_options,
    index=cloud_bias_options.index(bias_default)
)

# Instantiate engine and evaluate
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

# Main Layout
tab1, tab2, tab3 = st.tabs(["📊 Recommendation Summary", "🛠️ Action Checklist & CLI", "📖 Documentation Hub"])

with tab1:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown(f"### 🏆 Primary Winner: **{pri.service_name}**")
        st.markdown(f"**Cloud Provider:** `{pri.cloud_provider}` | **Tier:** `{pri.architecture_tier}`")
        
        # Fit score indicator
        st.progress(int(pri.fit_score), text=f"Architectural Fit Score: {pri.fit_score} / 100")
        
        st.success(f"💰 **Estimated Monthly Cost:** {pri.estimated_monthly_cost}")
        
        st.markdown("#### 💡 Strategic Justification")
        st.info(pri.why_recommended)
        
        col_adv, col_tro = st.columns(2)
        with col_adv:
            st.markdown("#### ✨ Key Advantages")
            for adv in pri.key_advantages:
                st.markdown(f"- {adv}")
                
        with col_tro:
            st.markdown("#### ⚠️ Trade-offs & Risks")
            for tro in pri.tradeoffs_and_risks:
                st.markdown(f"- {tro}")

        st.markdown("#### ⚡ Quickstart Deployment Command")
        st.code(pri.quickstart_cli_command, language="bash")

    with col_right:
        st.markdown(f"### 🥈 Runner-Up Option: **{run.service_name}**")
        st.markdown(f"**Cloud Provider:** `{run.cloud_provider}` | **Tier:** `{run.architecture_tier}`")
        st.progress(int(run.fit_score), text=f"Fit Score: {run.fit_score} / 100")
        st.warning(f"💰 **Estimated Cost:** {run.estimated_monthly_cost}")
        st.caption(f"**Why Runner-Up:** {run.why_recommended}")
        st.markdown(f"**Documentation Reference:** [`{run.doc_reference}`](./{run.doc_reference})")
        st.code(run.quickstart_cli_command, language="bash")
        
        if alt and alt.service_name != pri.service_name:
            st.divider()
            st.markdown(f"### 🏡 Zero-Cost / Edge Alternative")
            st.markdown(f"**Service:** `{alt.service_name}`")
            st.markdown(f"**Monthly Cloud Spend:** `{alt.estimated_monthly_cost}`")
            st.caption(alt.key_advantages[0])
            st.code(alt.quickstart_cli_command, language="bash")

with tab2:
    st.subheader("📋 Pre-Flight Deployment Checklist")
    st.write(result.architecture_decision_rationale)
    
    for idx, item in enumerate(result.action_checklist, 1):
        st.checkbox(item, key=f"checklist_item_{idx}")
        
    st.divider()
    st.subheader("📥 Export Recommendation as JSON")
    json_export = json.dumps(result.model_dump(), indent=2)
    st.download_button(
        label="Download Recommendation JSON",
        data=json_export,
        file_name=f"{app_name.lower().replace(' ', '_')}_deployment_strategy.json",
        mime="application/json"
    )

with tab3:
    st.subheader("📚 Architectural Guides & Production Blueprints")
    st.markdown(
        """
        Explore comprehensive platform-specific guides, comparative matrices, and step-by-step playbooks:
        * ⚙️ **[System Architecture & Engine Specification](./System_Architecture_and_Engine.md)**: MCDA formulas, Pydantic schemas, and validation tests.
        * 🛠️ **[Step-by-Step Production Playbooks](./Step_by_Step_Deployment_Guide.md)**: Concrete CLI commands, Dockerfiles, and flowcharts for all strategies.
        * 📊 **[Comparative Analysis & Decision Matrix](./Conclusion.md)**: 12-dimension head-to-head cloud comparison and scenario breakdowns.
        * ☁️ **[AWS Deployment Guide](./AWS_Deployment.md)**: App Runner, ECS Fargate, Lightsail, EC2 GPUs, and IAM roles.
        * 🔷 **[Azure Deployment Guide](./Azure_Deployment.md)**: Container Apps (ACA), App Service, Entra ID SSO, and Azure Files.
        * 🇬 **[GCP Deployment Guide](./GCP_Deployment.md)**: Cloud Run, GCS FUSE volumes, Cloud NAT, and G2 Spot GPUs.
        """
    )
