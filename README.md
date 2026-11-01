# 🚀 Cloud Deployment Strategies: AWS vs. Azure vs. GCP

Production deployment blueprints, automated decision system, architecture comparisons, and cost optimization guides for deploying containerized Python, Streamlit, FastAPI, and AI/ML applications across Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP).

---

## 🧭 Automated Strategy Recommendation Engine

This repository includes a multi-criteria decision engine that evaluates your application requirements (workload type, budget, traffic profile, GPU, enterprise SSO, and protocols) and returns tailored cloud deployment recommendations with cost estimates and copy-paste CLI commands.

### Quickstart

```bash
# 1. Interactive CLI Wizard
python recommend.py -i

# 2. Command-Line Direct Query
python recommend.py --app-name "YouTranscribe" --workload web_app --budget free_tier --protocol websocket

# 3. Interactive Web Dashboard
streamlit run app.py
```

---

## 📚 Documentation Index

| Guide | Description | Highlights Covered |
|---|---|---|
| ⚙️ **[`System_Architecture_and_Engine.md`](./System_Architecture_and_Engine.md)** | Decision Engine Architecture & Specification | Multi-Criteria Decision Analysis (MCDA), Pydantic input ontology, hard filters, soft scoring heuristics, and test cases. |
| 🛠️ **[`Step_by_Step_Deployment_Guide.md`](./Step_by_Step_Deployment_Guide.md)** | Production Deployment Playbooks | Copy-paste step-by-step deploy commands, flowcharts, Dockerfiles, Nginx SSL, and health checks for all 8 major strategies. |
| 📊 **[`Conclusion.md`](./Conclusion.md)** | Comparative Analysis & Decision Matrix | 12-dimension head-to-head matrix, 10 detailed real-world scenarios, cost models, and decision flowchart. |
| ☁️ **[`AWS_Deployment.md`](./AWS_Deployment.md)** | Amazon Web Services Architecture Guide | App Runner, ECS Fargate, EC2 (CPU/GPU), Lightsail, Lambda, WebSockets, ECR, and GitHub Actions CI/CD. |
| 🔷 **[`Azure_Deployment.md`](./Azure_Deployment.md)** | Microsoft Azure Architecture Guide | Azure Container Apps (ACA), App Service (B1/P1v3), NC-Series GPU VMs, Azure Files SMB volumes, and Entra ID SSO. |
| 🇬 **[`GCP_Deployment.md`](./GCP_Deployment.md)** | Google Cloud Platform Architecture Guide | Google Cloud Run, GCS FUSE volumes, Cloud NAT egress, Compute Engine G2 Spot GPUs (Nvidia L4), and GKE Autopilot. |

---

## 🏆 Scenario Winners Summary

| Scenario | Recommended Cloud & Service | Expected Monthly Cost | Key Advantage |
|---|---|---|---|
| **Low-Budget / Hobby / MVP (<$2/mo)** | **Google Cloud Run** | **$0.00 – $2.00** | 2M free requests/mo, true scale-to-zero, 2–5s cold start |
| **Predictable Fixed Flat Budget** | **AWS Lightsail** | **$3.50 – $5.00 flat** | Predictable monthly cost, 1TB–2TB free bandwidth |
| **Enterprise / Corporate SSO (M365)** | **Azure Container Apps / App Service** | **$15.00 – $55.00** | Zero-code Entra ID (Azure AD) authentication reverse proxy |
| **Dedicated GPU AI (Whisper, Ollama)** | **GCP Compute Engine G2 (`g2-standard-4`)** | **~$85/mo (Spot)** | 24GB VRAM Nvidia L4 Ada Lovelace GPU |
| **YouTube Scraper / Static Egress IP** | **Local (`run.bat`) / GCP Cloud Run + Cloud NAT** | **$0.00 / ~$10.00** | Residential IP or reserved static egress IP pool |
| **High-Scale Web APIs** | **Google Cloud Run** | **Pay-per-use** | Multi-concurrency (up to 1,000 reqs/instance) |
| **Kubernetes / Multi-Microservice** | **GCP GKE Autopilot** | **~$73/mo + vCPU** | Automated node provisioning, hardening, and auto-repair |

---

## 📄 License

This repository is licensed under the [MIT License](https://opensource.org/licenses/MIT).
