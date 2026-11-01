from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WorkloadType(str, Enum):
    WEB_APP = "web_app"                     # Streamlit, Dash, Next.js, React
    REST_API = "rest_api"                   # FastAPI, Express, Flask, Go
    AI_INFERENCE_GPU = "ai_inference_gpu"   # Ollama, Whisper, vLLM, PyTorch (Requires GPU)
    AI_INFERENCE_CPU = "ai_inference_cpu"   # Small models, ONNX, spaCy, CPU PyTorch
    SCRAPER_WORKER = "scraper_worker"       # YouTube transcript, crawler, strict egress IP
    EVENT_WORKER = "event_worker"           # Queue worker, SQS/PubSub, cron jobs
    MICROSERVICES = "microservices"         # Multi-service ecosystem, K8s

class BudgetTier(str, Enum):
    FREE_TIER = "free_tier"                 # Target $0 / month (Must leverage free tier)
    ULTRA_LOW = "ultra_low"                 # Target <$5 / month
    FLAT_BUDGET = "flat_budget"             # Predictable $3 - $15 / month, zero surprise bills
    STANDARD = "standard"                   # $20 - $80 / month, pay-as-you-go performance
    ENTERPRISE = "enterprise"               # $100+/month, high availability, strict SLAs

class TrafficPattern(str, Enum):
    SPORADIC = "sporadic"                   # Low or bursty, idle for hours/days (Scale-to-zero required)
    PREDICTABLE = "predictable"             # Steady daytime usage, known peaks
    HIGH_SUSTAINED = "high_sustained"       # 24/7 continuous high volume

class GPURequirement(str, Enum):
    NONE = "none"                           # CPU only
    LIGHT_GPU = "light_gpu"                 # 8GB - 16GB VRAM (e.g. Nvidia T4, Whisper base/medium)
    HEAVY_GPU = "heavy_gpu"                 # 24GB+ VRAM (e.g. Nvidia L4, A10G, 7B/14B LLMs)

class AuthRequirement(str, Enum):
    PUBLIC_NONE = "public_none"             # Public or application-managed auth (JWT, Firebase)
    MICROSOFT_ENTRA = "microsoft_entra"     # Deep Azure AD / Microsoft 365 SSO requirement
    AWS_IAM = "aws_iam"                     # AWS IAM roles & enterprise policies
    GCP_IAM = "gcp_iam"                     # Google Workspace / GCP Cloud IAM

class ProtocolRequirement(str, Enum):
    STANDARD_HTTP = "standard_http"         # Simple HTTP GET/POST, short timeouts (<30s)
    STREAMING_WEBSOCKET = "websocket"       # Long-lived WebSockets (Streamlit, SSE, chat streaming)
    BACKGROUND_TASK = "background_task"     # Long-running async execution (>15 mins)

class StorageRequirement(str, Enum):
    STATELESS = "stateless"                 # Ephemeral, no local disk needed across restarts
    PERSISTENT_VOLUME = "persistent_volume" # Mounted file storage (models, cache, sqlite, SMB/FUSE)
    MANAGED_DB = "managed_db"               # Connects to RDS / Cloud SQL / external DB

class SystemRequirements(BaseModel):
    app_name: str = Field(default="My Cloud Application", description="Human-readable application name")
    workload_type: WorkloadType = Field(default=WorkloadType.WEB_APP)
    budget_tier: BudgetTier = Field(default=BudgetTier.ULTRA_LOW)
    traffic_pattern: TrafficPattern = Field(default=TrafficPattern.SPORADIC)
    gpu_requirement: GPURequirement = Field(default=GPURequirement.NONE)
    auth_requirement: AuthRequirement = Field(default=AuthRequirement.PUBLIC_NONE)
    protocol: ProtocolRequirement = Field(default=ProtocolRequirement.STREAMING_WEBSOCKET)
    storage: StorageRequirement = Field(default=StorageRequirement.STATELESS)
    compliance_needed: bool = Field(default=False, description="HIPAA, FedRAMP, or GovCloud compliance")
    team_cloud_familiarity: Optional[str] = Field(default="any", description="aws, azure, gcp, or any")

class DeploymentOption(BaseModel):
    cloud_provider: str                     # "AWS", "Azure", "GCP", or "Local"
    service_name: str                       # e.g., "Google Cloud Run", "AWS Lightsail", "Azure Container Apps"
    architecture_tier: str                  # "Serverless Container", "Managed VPS", "Dedicated GPU VM", "Kubernetes"
    estimated_monthly_cost: str             # e.g., "$0.00 - $2.00 / month"
    fit_score: float                        # 0 to 100
    why_recommended: str                    # Summary justification
    key_advantages: List[str]
    tradeoffs_and_risks: List[str]
    quickstart_cli_command: str
    doc_reference: str                      # Link to respective markdown guide

class RecommendationResult(BaseModel):
    requirements_summary: SystemRequirements
    primary_strategy: DeploymentOption
    runner_up_strategy: DeploymentOption
    alternative_local_or_vps: Optional[DeploymentOption] = None
    architecture_decision_rationale: str
    action_checklist: List[str]

