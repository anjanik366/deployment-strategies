from typing import Dict, Any, List
from engine.models import (
    WorkloadType,
    BudgetTier,
    TrafficPattern,
    GPURequirement,
    AuthRequirement,
    ProtocolRequirement,
    StorageRequirement,
    DeploymentOption
)

SERVICES_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "gcp_cloud_run",
        "cloud": "GCP",
        "service": "Google Cloud Run",
        "tier": "Serverless Container",
        "min_cost": 0.0,
        "typical_cost": 1.50,
        "max_cost": 25.0,
        "supports_gpu": False,
        "supports_scale_to_zero": True,
        "supports_websockets": True,
        "websocket_timeout_sec": 3600,
        "supports_persistent_storage": True, # Via GCS FUSE
        "concurrency_per_instance": 1000,
        "free_tier_generous": True,
        "best_for": [
            WorkloadType.WEB_APP,
            WorkloadType.REST_API,
            WorkloadType.AI_INFERENCE_CPU,
            WorkloadType.SCRAPER_WORKER
        ],
        "key_advantages": [
            "Generous monthly free tier: 2M requests, 360k GB-sec, 180k vCPU-sec free.",
            "Instant scale-to-zero ($0 idle cost) with 2-4 second cold start.",
            "High concurrency: single instance handles up to 1,000 simultaneous WebSocket/HTTP requests.",
            "Built-in Cloud Storage (GCS) volume mount via FUSE without managing NFS."
        ],
        "tradeoffs": [
            "Cannot mount dedicated on-device GPUs (CPU/RAM only).",
            "Outbound IP is dynamic unless paired with Serverless VPC Access + Cloud NAT."
        ],
        "cli_command": "gcloud run deploy my-app --source . --region us-central1 --allow-unauthenticated --port 8501",
        "doc_ref": "GCP_Deployment.md"
    },
    {
        "id": "aws_lightsail",
        "cloud": "AWS",
        "service": "AWS Lightsail",
        "tier": "Managed VPS (Flat Fee)",
        "min_cost": 3.50,
        "typical_cost": 5.00,
        "max_cost": 10.00,
        "supports_gpu": False,
        "supports_scale_to_zero": False,
        "supports_websockets": True,
        "websocket_timeout_sec": 86400,
        "supports_persistent_storage": True,
        "concurrency_per_instance": 200,
        "free_tier_generous": False,
        "best_for": [
            WorkloadType.WEB_APP,
            WorkloadType.REST_API,
            WorkloadType.SCRAPER_WORKER,
            WorkloadType.AI_INFERENCE_CPU
        ],
        "key_advantages": [
            "100% predictable fixed flat pricing ($3.50 - $5.00/mo) with zero surprise bills.",
            "Includes 1TB - 2TB free data transfer allowance out to internet.",
            "Full root access (SSH, Docker, Docker Compose, Nginx, Certbot).",
            "Dedicated static public IPv4 address included for consistent scraping egress."
        ],
        "tradeoffs": [
            "Manual OS updates and security patching required.",
            "No automated horizontal auto-scaling (fixed vCPU/RAM envelope)."
        ],
        "cli_command": "aws lightsail create-instances --instance-names my-app --availability-zone us-east-1a --blueprint-id ubuntu_22_04 --bundle-id nano_2_0",
        "doc_ref": "AWS_Deployment.md"
    },
    {
        "id": "azure_container_apps",
        "cloud": "Azure",
        "service": "Azure Container Apps (ACA)",
        "tier": "Serverless Container (KEDA)",
        "min_cost": 0.0,
        "typical_cost": 8.00,
        "max_cost": 45.0,
        "supports_gpu": False, # Serverless tier
        "supports_scale_to_zero": True,
        "supports_websockets": True,
        "websocket_timeout_sec": 1800,
        "supports_persistent_storage": True, # Azure Files SMB
        "concurrency_per_instance": 300,
        "free_tier_generous": True,
        "best_for": [
            WorkloadType.WEB_APP,
            WorkloadType.REST_API,
            WorkloadType.EVENT_WORKER
        ],
        "key_advantages": [
            "Turnkey Entra ID (Azure AD) SSO authentication proxy without modifying code.",
            "Built on Kubernetes & KEDA with true scale-to-zero and microservice Dapr support.",
            "Native Azure Files SMB volume mount for persisting data/models across pod lifecycles.",
            "180,000 vCPU-seconds and 360,000 GiB-seconds monthly free allowance."
        ],
        "tradeoffs": [
            "Cold start slightly slower than GCP Cloud Run (15-25 seconds).",
            "CLI deployment syntax and Azure Resource Group management is more complex."
        ],
        "cli_command": "az containerapp up --name my-app --resource-group my-rg --source . --ingress external --target-port 8501",
        "doc_ref": "Azure_Deployment.md"
    },
    {
        "id": "aws_app_runner",
        "cloud": "AWS",
        "service": "AWS App Runner",
        "tier": "Fully Managed Container",
        "min_cost": 5.0,
        "typical_cost": 15.0,
        "max_cost": 65.0,
        "supports_gpu": False,
        "supports_scale_to_zero": False, # Memory billed continuously (~$4.50/mo)
        "supports_websockets": True,
        "websocket_timeout_sec": 3600,
        "supports_persistent_storage": False,
        "concurrency_per_instance": 100,
        "free_tier_generous": False,
        "best_for": [
            WorkloadType.WEB_APP,
            WorkloadType.REST_API
        ],
        "key_advantages": [
            "Zero VPC or ALB management required; hands-off AWS container PaaS.",
            "Automatic build and deployment directly from GitHub or AWS ECR.",
            "Native AWS IAM role integration for seamless access to S3, DynamoDB, Bedrock."
        ],
        "tradeoffs": [
            "No true $0 scale-to-zero; idle memory remains allocated ($4.50+/mo).",
            "Cannot mount persistent file volumes (EFS not supported)."
        ],
        "cli_command": "aws apprunner create-service --service-name my-app --source-configuration ...",
        "doc_ref": "AWS_Deployment.md"
    },
    {
        "id": "gcp_compute_gpu_l4",
        "cloud": "GCP",
        "service": "Compute Engine G2 GPU (Nvidia L4 24GB)",
        "tier": "Dedicated AI GPU Host",
        "min_cost": 85.0,
        "typical_cost": 120.0,
        "max_cost": 230.0,
        "supports_gpu": True,
        "supports_scale_to_zero": False,
        "supports_websockets": True,
        "websocket_timeout_sec": 86400,
        "supports_persistent_storage": True,
        "concurrency_per_instance": 50,
        "free_tier_generous": False,
        "best_for": [
            WorkloadType.AI_INFERENCE_GPU
        ],
        "key_advantages": [
            "Nvidia L4 24GB VRAM Ada Lovelace architecture: runs 7B/14B LLMs and Whisper large-v3.",
            "Spot VM pricing is exceptionally cost-effective (~$85/mo for 24GB VRAM).",
            "Google Deep Learning VM images come pre-installed with CUDA 12, PyTorch, and Ollama.",
            "Highest bandwidth and token throughput in its price category."
        ],
        "tradeoffs": [
            "Spot VMs can be preempted; requires automated checkpointing and systemd auto-restart.",
            "Higher baseline cost than serverless CPU containers."
        ],
        "cli_command": "gcloud compute instances create ai-gpu-host --zone us-central1-a --machine-type g2-standard-4 --accelerator type=nvidia-l4,count=1 --provisioning-model=SPOT",
        "doc_ref": "GCP_Deployment.md"
    },
    {
        "id": "aws_ec2_gpu_t4",
        "cloud": "AWS",
        "service": "AWS EC2 g4dn.xlarge (Nvidia T4 16GB)",
        "tier": "Dedicated AI GPU Host",
        "min_cost": 115.0,
        "typical_cost": 150.0,
        "max_cost": 380.0,
        "supports_gpu": True,
        "supports_scale_to_zero": False,
        "supports_websockets": True,
        "websocket_timeout_sec": 86400,
        "supports_persistent_storage": True,
        "concurrency_per_instance": 40,
        "free_tier_generous": False,
        "best_for": [
            WorkloadType.AI_INFERENCE_GPU
        ],
        "key_advantages": [
            "AWS Deep Learning AMI with pre-configured Nvidia Container Toolkit and drivers.",
            "Deep integration with Amazon S3 and AWS IAM instance profiles.",
            "Proven reliability for Whisper, FastPitch, and moderate PyTorch workloads."
        ],
        "tradeoffs": [
            "16GB VRAM Turing architecture is older and slower than GCP's 24GB Nvidia L4.",
            "Spot pricing (~$115/mo) is ~35% more expensive than GCP L4 Spot."
        ],
        "cli_command": "aws ec2 run-instances --image-id ami-0123456789 --instance-type g4dn.xlarge --instance-market-options 'MarketType=spot'",
        "doc_ref": "AWS_Deployment.md"
    },
    {
        "id": "local_production_tunnel",
        "cloud": "Local",
        "service": "Local Hardware + Cloudflare / Localtunnel",
        "tier": "Zero-Cost Edge Production",
        "min_cost": 0.0,
        "typical_cost": 0.0,
        "max_cost": 0.0,
        "supports_gpu": True,
        "supports_scale_to_zero": False,
        "supports_websockets": True,
        "websocket_timeout_sec": 86400,
        "supports_persistent_storage": True,
        "concurrency_per_instance": 100,
        "free_tier_generous": True,
        "best_for": [
            WorkloadType.SCRAPER_WORKER,
            WorkloadType.AI_INFERENCE_GPU,
            WorkloadType.WEB_APP
        ],
        "key_advantages": [
            "100% Free ($0.00 cloud invoice) leveraging existing local CPU/GPU hardware.",
            "Residential ISP IP address is immune to YouTube/Cloudflare datacenter IP blocking.",
            "Zero cloud data egress charges or bandwidth limits.",
            "Instant testing and zero Docker image push/pull overhead."
        ],
        "tradeoffs": [
            "Dependent on home/office power and internet connection uptime.",
            "Requires machine to remain awake 24/7 for public access."
        ],
        "cli_command": "run.bat (Option 2) or cloudflared tunnel run my-tunnel",
        "doc_ref": "Conclusion.md"
    },
    {
        "id": "gcp_gke_autopilot",
        "cloud": "GCP",
        "service": "Google Kubernetes Engine (GKE) Autopilot",
        "tier": "Fully Managed Kubernetes",
        "min_cost": 73.0,
        "typical_cost": 140.0,
        "max_cost": 600.0,
        "supports_gpu": True,
        "supports_scale_to_zero": False,
        "supports_websockets": True,
        "websocket_timeout_sec": 86400,
        "supports_persistent_storage": True,
        "concurrency_per_instance": 2000,
        "free_tier_generous": False,
        "best_for": [
            WorkloadType.MICROSERVICES
        ],
        "key_advantages": [
            "Fully automated node management, security patching, and multi-tenant isolation.",
            "Pay solely for requested pod vCPU/RAM; zero unutilized compute overhead.",
            "World-class GitOps and Kubernetes ecosystem compatibility."
        ],
        "tradeoffs": [
            "Baseline cluster management fee (~$73/mo).",
            "High architectural complexity for single-container applications."
        ],
        "cli_command": "gcloud container clusters create-auto my-cluster --region us-central1",
        "doc_ref": "GCP_Deployment.md"
    }
]
