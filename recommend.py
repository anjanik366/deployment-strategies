#!/usr/bin/env python3
"""
recommend.py - Deployment Strategy Recommendation Engine CLI
Takes system requirements and recommends optimal cloud deployment strategies.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

# Ensure repository root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Ensure UTF-8 output in Windows PowerShell / Command Prompt
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from engine.models import (
    SystemRequirements,
    WorkloadType,
    BudgetTier,
    TrafficPattern,
    GPURequirement,
    AuthRequirement,
    ProtocolRequirement,
    StorageRequirement,
    RecommendationResult
)
from engine.decision_engine import DecisionEngine

def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Recommend the optimal cloud deployment strategy based on system requirements."
    )
    parser.add_argument("--interactive", "-i", action="store_true", help="Launch interactive requirement wizard")
    parser.add_argument("--app-name", type=str, default="Cloud App", help="Name of your application")
    parser.add_argument(
        "--workload",
        type=str,
        choices=[e.value for e in WorkloadType],
        default=WorkloadType.WEB_APP.value,
        help="Type of workload (web_app, rest_api, ai_inference_gpu, scraper_worker, etc.)"
    )
    parser.add_argument(
        "--budget",
        type=str,
        choices=[e.value for e in BudgetTier],
        default=BudgetTier.ULTRA_LOW.value,
        help="Budget tier (free_tier, ultra_low, flat_budget, standard, enterprise)"
    )
    parser.add_argument(
        "--traffic",
        type=str,
        choices=[e.value for e in TrafficPattern],
        default=TrafficPattern.SPORADIC.value,
        help="Traffic pattern (sporadic, predictable, high_sustained)"
    )
    parser.add_argument(
        "--gpu",
        type=str,
        choices=[e.value for e in GPURequirement],
        default=GPURequirement.NONE.value,
        help="GPU requirement (none, light_gpu, heavy_gpu)"
    )
    parser.add_argument(
        "--auth",
        type=str,
        choices=[e.value for e in AuthRequirement],
        default=AuthRequirement.PUBLIC_NONE.value,
        help="Authentication requirement (public_none, microsoft_entra, aws_iam, gcp_iam)"
    )
    parser.add_argument(
        "--protocol",
        type=str,
        choices=[e.value for e in ProtocolRequirement],
        default=ProtocolRequirement.STREAMING_WEBSOCKET.value,
        help="Protocol requirement (standard_http, websocket, background_task)"
    )
    parser.add_argument(
        "--storage",
        type=str,
        choices=[e.value for e in StorageRequirement],
        default=StorageRequirement.STATELESS.value,
        help="Storage persistence requirement (stateless, persistent_volume, managed_db)"
    )
    parser.add_argument("--cloud-bias", type=str, default="any", help="Preferred cloud (aws, azure, gcp, any)")
    parser.add_argument("--json-output", action="store_true", help="Output raw JSON instead of formatted text")
    parser.add_argument("--json-file", type=str, help="Load requirements from a JSON file")

    return parser.parse_args()

def interactive_wizard() -> SystemRequirements:
    print("\n" + "="*60)
    print("🛠️  CLOUD DEPLOYMENT STRATEGY REQUIREMENT WIZARD")
    print("="*60 + "\n")

    app_name = input("1. Application Name [My Application]: ").strip() or "My Application"

    print("\n2. Workload Type:")
    w_options = list(WorkloadType)
    for idx, opt in enumerate(w_options, 1):
        print(f"   [{idx}] {opt.value}")
    w_choice = input(f"Select (1-{len(w_options)}) [1]: ").strip() or "1"
    workload = w_options[int(w_choice)-1] if w_choice.isdigit() and 1 <= int(w_choice) <= len(w_options) else WorkloadType.WEB_APP

    print("\n3. Budget / Cost Sensitivity:")
    b_options = list(BudgetTier)
    for idx, opt in enumerate(b_options, 1):
        print(f"   [{idx}] {opt.value}")
    b_choice = input(f"Select (1-{len(b_options)}) [2]: ").strip() or "2"
    budget = b_options[int(b_choice)-1] if b_choice.isdigit() and 1 <= int(b_choice) <= len(b_options) else BudgetTier.ULTRA_LOW

    print("\n4. Traffic Profile:")
    t_options = list(TrafficPattern)
    for idx, opt in enumerate(t_options, 1):
        print(f"   [{idx}] {opt.value}")
    t_choice = input(f"Select (1-{len(t_options)}) [1]: ").strip() or "1"
    traffic = t_options[int(t_choice)-1] if t_choice.isdigit() and 1 <= int(t_choice) <= len(t_options) else TrafficPattern.SPORADIC

    print("\n5. GPU Acceleration:")
    g_options = list(GPURequirement)
    for idx, opt in enumerate(g_options, 1):
        print(f"   [{idx}] {opt.value}")
    g_choice = input(f"Select (1-{len(g_options)}) [1]: ").strip() or "1"
    gpu = g_options[int(g_choice)-1] if g_choice.isdigit() and 1 <= int(g_choice) <= len(g_options) else GPURequirement.NONE

    print("\n6. Enterprise Authentication Ecosystem:")
    a_options = list(AuthRequirement)
    for idx, opt in enumerate(a_options, 1):
        print(f"   [{idx}] {opt.value}")
    a_choice = input(f"Select (1-{len(a_options)}) [1]: ").strip() or "1"
    auth = a_options[int(a_choice)-1] if a_choice.isdigit() and 1 <= int(a_choice) <= len(a_options) else AuthRequirement.PUBLIC_NONE

    print("\n7. Protocol & Connection Lifetime:")
    p_options = list(ProtocolRequirement)
    for idx, opt in enumerate(p_options, 1):
        print(f"   [{idx}] {opt.value}")
    p_choice = input(f"Select (1-{len(p_options)}) [2]: ").strip() or "2"
    protocol = p_options[int(p_choice)-1] if p_choice.isdigit() and 1 <= int(p_choice) <= len(p_options) else ProtocolRequirement.STREAMING_WEBSOCKET

    print("\n8. Preferred Cloud Provider (if any):")
    cloud_bias = input("Enter 'aws', 'azure', 'gcp', or 'any' [any]: ").strip().lower() or "any"

    return SystemRequirements(
        app_name=app_name,
        workload_type=workload,
        budget_tier=budget,
        traffic_pattern=traffic,
        gpu_requirement=gpu,
        auth_requirement=auth,
        protocol=protocol,
        team_cloud_familiarity=cloud_bias
    )

def print_result_banner(result: RecommendationResult):
    pri = result.primary_strategy
    run = result.runner_up_strategy
    req = result.requirements_summary

    print("\n" + "="*70)
    print(f"🎯 DEPLOYMENT STRATEGY RECOMMENDATION FOR: {req.app_name.upper()}")
    print("="*70)

    print(f"\n📋 Input Requirements Summary:")
    print(f"  • Workload:        {req.workload_type.value}")
    print(f"  • Budget Tier:     {req.budget_tier.value}")
    print(f"  • Traffic Pattern: {req.traffic_pattern.value}")
    print(f"  • GPU Required:    {req.gpu_requirement.value}")
    print(f"  • Auth / Identity: {req.auth_requirement.value}")
    print(f"  • Protocol:        {req.protocol.value}")

    print("\n" + "-"*70)
    print(f"🏆 PRIMARY STRATEGY: {pri.service_name} ({pri.cloud_provider})")
    print(f"   Fit Score: {pri.fit_score}/100 | Tier: {pri.architecture_tier}")
    print(f"   Estimated Cost: {pri.estimated_monthly_cost}")
    print("-" * 70)
    print(f"💡 Why Recommended:\n   {pri.why_recommended}")
    print("\n✨ Key Advantages:")
    for adv in pri.key_advantages:
        print(f"   • {adv}")
    print("\n⚠️ Trade-offs & Risks:")
    for tro in pri.tradeoffs_and_risks:
        print(f"   • {tro}")
    print(f"\n⚡ Quickstart Deployment Command:")
    print(f"   $ {pri.quickstart_cli_command}")
    print(f"\n📖 Detailed Implementation Guide: {pri.doc_reference}")

    print("\n" + "-"*70)
    print(f"🥈 RUNNER-UP STRATEGY: {run.service_name} ({run.cloud_provider})")
    print(f"   Fit Score: {run.fit_score}/100 | Estimated Cost: {run.estimated_monthly_cost}")
    print(f"   Why Runner-Up: {run.why_recommended}")
    print(f"   Guide: {run.doc_reference}")
    print("-" * 70)

    if result.alternative_local_or_vps:
        alt = result.alternative_local_or_vps
        print("\n" + "-"*70)
        print(f"🏡 ZERO-COST / EDGE ALTERNATIVE: {alt.service_name}")
        print(f"   Cost: {alt.estimated_monthly_cost} | Advantage: {alt.key_advantages[0]}")
        print(f"   Run Command: {alt.quickstart_cli_command}")
        print("-" * 70)

    print("\n📝 ACTION CHECKLIST:")
    for step in result.action_checklist:
        print(f"   {step}")
    print("\n" + "="*70 + "\n")

def main():
    args = parse_cli_args()
    engine = DecisionEngine()

    if args.json_file:
        with open(args.json_file, "r") as f:
            data = json.load(f)
        reqs = SystemRequirements(**data)
    elif args.interactive or len(sys.argv) == 1:
        reqs = interactive_wizard()
    else:
        reqs = SystemRequirements(
            app_name=args.app_name,
            workload_type=WorkloadType(args.workload),
            budget_tier=BudgetTier(args.budget),
            traffic_pattern=TrafficPattern(args.traffic),
            gpu_requirement=GPURequirement(args.gpu),
            auth_requirement=AuthRequirement(args.auth),
            protocol=ProtocolRequirement(args.protocol),
            storage=StorageRequirement(args.storage),
            team_cloud_familiarity=args.cloud_bias
        )

    result = engine.evaluate(reqs)

    if args.json_output:
        print(json.dumps(result.model_dump(), indent=2))
    else:
        print_result_banner(result)

if __name__ == "__main__":
    main()
