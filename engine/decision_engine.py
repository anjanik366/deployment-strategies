from typing import List, Tuple, Dict, Any
from engine.models import (
    SystemRequirements,
    RecommendationResult,
    DeploymentOption,
    WorkloadType,
    BudgetTier,
    TrafficPattern,
    GPURequirement,
    AuthRequirement,
    ProtocolRequirement,
    StorageRequirement
)
from engine.rules import SERVICES_CATALOG

class DecisionEngine:
    """
    Multi-Criteria Decision Engine for Cloud Deployments.
    Evaluates hard constraints, applies domain scoring heuristics, and returns
    tailored primary, runner-up, and edge deployment strategies.
    """

    def __init__(self, catalog: List[Dict[str, Any]] = None):
        self.catalog = catalog or SERVICES_CATALOG

    def evaluate(self, req: SystemRequirements) -> RecommendationResult:
        scored_candidates: List[Tuple[float, Dict[str, Any], List[str]]] = []

        for service in self.catalog:
            score, reasons = self._score_service(service, req)
            if score > 0: # Only keep valid non-disqualified candidates
                scored_candidates.append((score, service, reasons))

        # Sort descending by fit score
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        if not scored_candidates:
            # Fallback in case of hyper-constrained inputs
            primary = self._format_option(self.catalog[0], 50.0, ["Default fallback option."])
            runner_up = self._format_option(self.catalog[1], 40.0, ["Secondary fallback option."])
        else:
            best_score, best_srv, best_reasons = scored_candidates[0]
            primary = self._format_option(best_srv, best_score, best_reasons)

            if len(scored_candidates) > 1:
                ru_score, ru_srv, ru_reasons = scored_candidates[1]
                runner_up = self._format_option(ru_srv, ru_score, ru_reasons)
            else:
                runner_up = primary

        # Identify local edge option if not already primary
        local_opt = None
        for score, srv, reasons in scored_candidates:
            if srv["id"] == "local_production_tunnel" and srv["id"] != primary.service_name:
                local_opt = self._format_option(srv, score, reasons)
                break

        # Generate architectural decision rationale
        rationale = self._generate_rationale(req, primary, runner_up)
        checklist = self._generate_checklist(req, primary)

        return RecommendationResult(
            requirements_summary=req,
            primary_strategy=primary,
            runner_up_strategy=runner_up,
            alternative_local_or_vps=local_opt,
            architecture_decision_rationale=rationale,
            action_checklist=checklist
        )

    def _score_service(self, srv: Dict[str, Any], req: SystemRequirements) -> Tuple[float, List[str]]:
        score = 50.0
        reasons = []

        # --- HARD CONSTRAINT FILTERS ---
        # 1. GPU Requirement
        if req.gpu_requirement in [GPURequirement.LIGHT_GPU, GPURequirement.HEAVY_GPU]:
            if not srv["supports_gpu"]:
                return 0.0, ["Disqualified: Workload requires dedicated GPU acceleration."]
            if req.gpu_requirement == GPURequirement.HEAVY_GPU and srv["id"] == "aws_ec2_gpu_t4":
                score -= 20.0
                reasons.append("T4 (16GB) is under-sized for heavy 24GB+ LLM workloads compared to Nvidia L4.")
            if req.gpu_requirement == GPURequirement.HEAVY_GPU and srv["id"] == "gcp_compute_gpu_l4":
                score += 35.0
                reasons.append("Perfect match: 24GB VRAM Nvidia L4 handles 7B/14B parameter models natively.")
        else:
            # If no GPU required, dedicated GPU hosts are penalized heavily for cost inefficiency
            if srv["tier"] == "Dedicated AI GPU Host":
                score -= 40.0
                reasons.append("Overkill: Dedicated GPU instance is not cost-efficient for CPU-only workloads.")

        # 2. Strict Free Tier ($0) Budget
        if req.budget_tier == BudgetTier.FREE_TIER:
            if srv["min_cost"] > 0.0:
                return 0.0, ["Disqualified: Service requires a baseline monthly spend > $0."]
            score += 25.0
            reasons.append("Qualifies for zero-cost operation via permanent monthly free allowances.")

        # 3. Flat Predictable Budget
        if req.budget_tier == BudgetTier.FLAT_BUDGET:
            if srv["tier"] == "Managed VPS (Flat Fee)":
                score += 35.0
                reasons.append("Guarantees fixed predictable billing ($3.50-$5.00/mo) with zero surprise costs.")
            elif srv["tier"] == "Serverless Container":
                score += 10.0

        # 4. Workload Domain Alignment
        if req.workload_type in srv["best_for"]:
            score += 20.0
            reasons.append(f"Optimized architecture for {req.workload_type.value} workloads.")

        # 5. Scale to zero & Traffic Patterns
        if req.traffic_pattern == TrafficPattern.SPORADIC:
            if srv["supports_scale_to_zero"]:
                score += 25.0
                reasons.append("Native scale-to-zero stops 100% of compute billing during idle windows.")
            else:
                score -= 15.0
                reasons.append("Lacks scale-to-zero; instance runs and accrues charges 24/7 even when idle.")

        # 6. WebSocket & Streaming Support
        if req.protocol == ProtocolRequirement.STREAMING_WEBSOCKET:
            if srv["supports_websockets"]:
                score += 15.0
                reasons.append(f"Supports long-lived WebSockets with timeouts up to {srv['websocket_timeout_sec']}s.")
            else:
                return 0.0, ["Disqualified: Protocol requires WebSocket streaming."]

        # 7. Microsoft Entra ID SSO Affinity
        if req.auth_requirement == AuthRequirement.MICROSOFT_ENTRA:
            if srv["cloud"] == "Azure":
                score += 40.0
                reasons.append("Built-in zero-code Microsoft Entra ID (Azure AD) SSO reverse proxy authentication.")
            else:
                score -= 20.0
                reasons.append("Requires manual OpenID Connect code integration to authenticate against Azure AD.")

        # 8. Scraper Workload (YouTube / Web)
        if req.workload_type == WorkloadType.SCRAPER_WORKER:
            if srv["id"] == "local_production_tunnel":
                score += 35.0
                reasons.append("Residential IP eliminates YouTube anti-bot and datacenter IP rate limits.")
            elif srv["id"] == "aws_lightsail":
                score += 20.0
                reasons.append("Dedicated static IPv4 included without requiring a Cloud NAT gateway.")
            elif srv["id"] == "gcp_cloud_run":
                score += 10.0
                reasons.append("Highly scalable for scraping when routed through Cloud NAT.")

        # 9. Microservices Architecture
        if req.workload_type == WorkloadType.MICROSERVICES:
            if srv["tier"] == "Fully Managed Kubernetes":
                score += 30.0
                reasons.append("Standardized Kubernetes primitives, ingress controllers, and pod autoscaling.")
            elif srv["id"] == "azure_container_apps":
                score += 25.0
                reasons.append("Built-in Dapr microservices mesh and KEDA event-driven scaling.")

        # 10. Team Cloud Familiarity Bias
        if req.team_cloud_familiarity and req.team_cloud_familiarity.lower() != "any":
            if srv["cloud"].lower() == req.team_cloud_familiarity.lower():
                score += 15.0
                reasons.append(f"Aligns with existing team expertise in {srv['cloud']}.")

        # Normalize score between 10.0 and 99.0
        normalized_score = max(10.0, min(99.0, round(score, 1)))
        return normalized_score, reasons

    def _format_option(self, srv: Dict[str, Any], score: float, reasons: List[str]) -> DeploymentOption:
        cost_str = f"${srv['min_cost']:.2f} - ${srv['typical_cost']:.2f} / month"
        if srv['min_cost'] == 0.0:
            cost_str = f"$0.00 (Free Tier) to ${srv['typical_cost']:.2f} / month"

        return DeploymentOption(
            cloud_provider=srv["cloud"],
            service_name=srv["service"],
            architecture_tier=srv["tier"],
            estimated_monthly_cost=cost_str,
            fit_score=score,
            why_recommended="; ".join(reasons[:2]),
            key_advantages=srv["key_advantages"],
            tradeoffs_and_risks=srv["tradeoffs"],
            quickstart_cli_command=srv["cli_command"],
            doc_reference=srv["doc_ref"]
        )

    def _generate_rationale(self, req: SystemRequirements, primary: DeploymentOption, runner_up: DeploymentOption) -> str:
        return (
            f"For application '{req.app_name}' with workload '{req.workload_type.value}' and budget '{req.budget_tier.value}', "
            f"**{primary.service_name} ({primary.cloud_provider})** achieved the highest fit score ({primary.fit_score}/100). "
            f"It directly satisfies your {req.protocol.value} protocol needs and {req.traffic_pattern.value} traffic profile with estimated "
            f"monthly operating costs of {primary.estimated_monthly_cost}. "
            f"If {primary.cloud_provider} is unavailable or your team prefers an alternative, **{runner_up.service_name} ({runner_up.cloud_provider})** "
            f"is the recommended runner-up (fit score {runner_up.fit_score}/100)."
        )

    def _generate_checklist(self, req: SystemRequirements, primary: DeploymentOption) -> List[str]:
        checklist = [
            f"1. Authenticate with {primary.cloud_provider} CLI using administrative or deployment credentials.",
            "2. Containerize the application: ensure Dockerfile exposes the correct PORT environment variable.",
            f"3. Verify WebSocket configuration: ensure upstream proxy supports persistent HTTP/1.1 connections.",
            f"4. Run pre-flight deployment test: execute `{primary.quickstart_cli_command}`.",
            "5. Configure health check probes (/healthz or root endpoint) and domain SSL certificates.",
            f"6. Consult full step-by-step implementation guide: refer to `{primary.doc_reference}`."
        ]
        if req.gpu_requirement != GPURequirement.NONE:
            checklist.insert(3, "Verify Nvidia GPU driver and Container Toolkit (`nvidia-smi` and CUDA 12.x).")
        if req.auth_requirement == AuthRequirement.MICROSOFT_ENTRA:
            checklist.insert(4, "Configure App Registration in Microsoft Entra ID and assign User/Group roles.")
        return checklist

