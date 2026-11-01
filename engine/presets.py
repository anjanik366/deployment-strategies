"""
Predefined application requirement presets for rapid strategy evaluation.
"""
from typing import Dict, Any, List
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

PRESET_PROFILES: Dict[str, Dict[str, Any]] = {
    "Custom (Configure Below)": {
        "description": "Manually tune all technical, financial, and protocol parameters.",
        "requirements": None
    },
    "1. Streamlit MVP / Free Tier (<$2/mo)": {
        "description": "Serverless web UI with WebSocket streaming, sporadic usage, and scale-to-zero at $0 idle cost.",
        "requirements": SystemRequirements(
            app_name="Streamlit MVP",
            workload_type=WorkloadType.WEB_APP,
            budget_tier=BudgetTier.FREE_TIER,
            traffic_pattern=TrafficPattern.SPORADIC,
            gpu_requirement=GPURequirement.NONE,
            auth_requirement=AuthRequirement.PUBLIC_NONE,
            protocol=ProtocolRequirement.STREAMING_WEBSOCKET,
            storage=StorageRequirement.STATELESS,
            team_cloud_familiarity="any"
        )
    },
    "2. Dedicated GPU AI Host (Ollama / Whisper Large / 24GB)": {
        "description": "Heavy local AI inference requiring 24GB VRAM for 7B/14B parameter LLMs and Whisper large-v3.",
        "requirements": SystemRequirements(
            app_name="AI GPU Host",
            workload_type=WorkloadType.AI_INFERENCE_GPU,
            budget_tier=BudgetTier.STANDARD,
            traffic_pattern=TrafficPattern.PREDICTABLE,
            gpu_requirement=GPURequirement.HEAVY_GPU,
            auth_requirement=AuthRequirement.PUBLIC_NONE,
            protocol=ProtocolRequirement.STREAMING_WEBSOCKET,
            storage=StorageRequirement.PERSISTENT_VOLUME,
            team_cloud_familiarity="any"
        )
    },
    "3. Enterprise Internal SaaS (Microsoft 365 / Entra ID SSO)": {
        "description": "Corporate application requiring turnkey Azure Active Directory single sign-on without writing auth code.",
        "requirements": SystemRequirements(
            app_name="Corporate Portal",
            workload_type=WorkloadType.WEB_APP,
            budget_tier=BudgetTier.ENTERPRISE,
            traffic_pattern=TrafficPattern.HIGH_SUSTAINED,
            gpu_requirement=GPURequirement.NONE,
            auth_requirement=AuthRequirement.MICROSOFT_ENTRA,
            protocol=ProtocolRequirement.STREAMING_WEBSOCKET,
            storage=StorageRequirement.PERSISTENT_VOLUME,
            team_cloud_familiarity="azure"
        )
    },
    "4. YouTube Scraper / Egress-Sensitive Crawler": {
        "description": "Web scraping workload requiring residential IP or static egress NAT to avoid 429 rate-limiting.",
        "requirements": SystemRequirements(
            app_name="YouTube Scraper",
            workload_type=WorkloadType.SCRAPER_WORKER,
            budget_tier=BudgetTier.ULTRA_LOW,
            traffic_pattern=TrafficPattern.SPORADIC,
            gpu_requirement=GPURequirement.NONE,
            auth_requirement=AuthRequirement.PUBLIC_NONE,
            protocol=ProtocolRequirement.STANDARD_HTTP,
            storage=StorageRequirement.STATELESS,
            team_cloud_familiarity="any"
        )
    },
    "5. Fixed Flat-Budget VPS ($3.50 - $5.00/mo flat)": {
        "description": "Predictable monthly spend with 1TB-2TB bundled bandwidth, Docker Compose, and zero surprise billing.",
        "requirements": SystemRequirements(
            app_name="Flat VPS Service",
            workload_type=WorkloadType.WEB_APP,
            budget_tier=BudgetTier.FLAT_BUDGET,
            traffic_pattern=TrafficPattern.PREDICTABLE,
            gpu_requirement=GPURequirement.NONE,
            auth_requirement=AuthRequirement.PUBLIC_NONE,
            protocol=ProtocolRequirement.STREAMING_WEBSOCKET,
            storage=StorageRequirement.PERSISTENT_VOLUME,
            team_cloud_familiarity="aws"
        )
    },
    "6. High-Scale Containerized REST API": {
        "description": "FastAPI / Node.js backend requiring multi-concurrency (up to 1,000 reqs/container) and sub-second scaling.",
        "requirements": SystemRequirements(
            app_name="High-Scale API",
            workload_type=WorkloadType.REST_API,
            budget_tier=BudgetTier.STANDARD,
            traffic_pattern=TrafficPattern.HIGH_SUSTAINED,
            gpu_requirement=GPURequirement.NONE,
            auth_requirement=AuthRequirement.PUBLIC_NONE,
            protocol=ProtocolRequirement.STANDARD_HTTP,
            storage=StorageRequirement.MANAGED_DB,
            team_cloud_familiarity="gcp"
        )
    },
    "7. Multi-Microservices / Kubernetes Cluster": {
        "description": "Distributed microservices needing standardized Ingress, horizontal pod autoscaling, and service mesh.",
        "requirements": SystemRequirements(
            app_name="Microservices Mesh",
            workload_type=WorkloadType.MICROSERVICES,
            budget_tier=BudgetTier.ENTERPRISE,
            traffic_pattern=TrafficPattern.HIGH_SUSTAINED,
            gpu_requirement=GPURequirement.NONE,
            auth_requirement=AuthRequirement.PUBLIC_NONE,
            protocol=ProtocolRequirement.STANDARD_HTTP,
            storage=StorageRequirement.MANAGED_DB,
            team_cloud_familiarity="any"
        )
    }
}
