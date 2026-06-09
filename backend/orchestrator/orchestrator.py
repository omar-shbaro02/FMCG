"""
Orchestrator: Manages sequential execution of all 6 agents
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI

# Import agent modules
from agents.agent_1_intent import create_agent_1_prompt, parse_agent_1_response
from agents.agent_2_concentration import create_agent_2_prompt, parse_agent_2_response
from agents.agent_3_margin import create_agent_3_prompt, parse_agent_3_response
from agents.agent_4_demand import create_agent_4_prompt, parse_agent_4_response
from agents.agent_5_governance import create_agent_5_prompt, parse_agent_5_response
from agents.agent_6_brain import create_agent_6_prompt, parse_agent_6_response


class AgentOrchestrator:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        self.audit_log = []

    def _risk_level(self, score: int) -> str:
        if score >= 8:
            return "critical"
        if score >= 6:
            return "high"
        if score >= 3:
            return "medium"
        return "low"

    def _rule_based_analysis(self, case_data: Dict[str, Any], reason: str) -> Dict[str, Any]:
        self.audit_log = []

        baseline = float(case_data.get("baseline_sales_volume") or 0)
        promo = float(case_data.get("promotion_sales_volume") or 0)
        sell_in = float(case_data.get("sell_in_volume") or 0)
        sell_out = float(case_data.get("sell_out_volume") or 0)
        post = float(case_data.get("post_promotion_demand") or 0)
        key_account = float(case_data.get("key_account_contribution_percent") or 0)
        channel = float(case_data.get("channel_contribution_percent") or 0)
        customers = int(case_data.get("num_participating_customers") or 0)
        discount = float(case_data.get("discount_percent") or 0)
        trade_spend = float(case_data.get("trade_spend") or 0)
        margin_before = float(case_data.get("gross_margin_before") or 0)
        margin_during = float(case_data.get("gross_margin_during") or 0)
        forecast_variance = float(case_data.get("forecast_variance") or 0)
        data_quality = float(case_data.get("data_quality_confidence") or 0)

        uplift = ((promo - baseline) / baseline * 100) if baseline else float(case_data.get("uplift_percent") or 0)
        sell_gap = max(sell_in - sell_out, 0)
        sell_gap_percent = (sell_gap / sell_in * 100) if sell_in else 0
        post_delta = ((post - baseline) / baseline * 100) if baseline else 0
        margin_erosion = margin_before - margin_during
        incremental_units = max(promo - baseline, 1)
        spend_per_incremental_unit = trade_spend / incremental_units

        score = 0
        score += 3 if key_account >= 75 else 2 if key_account >= 55 else 1 if key_account >= 40 else 0
        score += 2 if channel >= 65 else 1 if channel >= 50 else 0
        score += 3 if sell_gap_percent >= 45 else 2 if sell_gap_percent >= 20 else 1 if sell_gap_percent >= 8 else 0
        score += 3 if post_delta <= -25 else 2 if post_delta <= -10 else 1 if post_delta < 0 else 0
        score += 2 if discount >= 25 else 1 if discount >= 15 else 0
        score += 3 if margin_during < 0 else 2 if margin_erosion >= 20 else 1 if margin_erosion >= 8 else 0
        score += 2 if forecast_variance >= 35 else 1 if forecast_variance >= 15 else 0
        score += 1 if customers and customers < 150 else 0

        severity = self._risk_level(score)
        if score >= 11:
            growth_health = "misleading"
            sustainability = "unsustainable"
            recommended_action = "Do not report this as sustainable growth. Freeze repeat promotions until sell-out, margin, and account concentration are reset."
        elif score >= 7:
            growth_health = "distortionary"
            sustainability = "unsustainable"
            recommended_action = "Pause expansion of this promotional model and run a retailer/account reset focused on sell-out and margin recovery."
        elif score >= 4:
            growth_health = "fragile"
            sustainability = "at_risk"
            recommended_action = "Continue only with tighter account spread, sell-out validation, and post-promotion demand monitoring."
        else:
            growth_health = "healthy"
            sustainability = "sustainable"
            recommended_action = "Use as a controlled promotion benchmark while continuing normal post-promotion monitoring."

        confidence = max(0.45, min(0.92, data_quality / 100 - (0.08 if reason else 0)))

        agents = {
            "agent_1": {
                "campaign_intent": case_data.get("campaign_objective") or "promotion performance review",
                "evaluation_lens": "promotion_health_and_distortion_risk",
                "risk_tolerance": "high" if discount >= 20 or uplift >= 100 else "moderate",
                "commercial_context_flags": [
                    flag for flag, active in {
                        "high_uplift_claim": uplift >= 75,
                        "heavy_discounting": discount >= 20,
                        "low_data_confidence": data_quality < 70,
                    }.items() if active
                ],
                "intent_clarity": "clear" if case_data.get("campaign_objective") else "limited",
                "confidence": confidence,
                "handoff_note": "Rule-based fallback used because " + reason,
            },
            "agent_2": {
                "growth_distribution": {
                    "key_account_percent": key_account,
                    "channel_percent": channel,
                    "participating_customers": customers,
                },
                "main_concentration_source": "key_account" if key_account >= channel else "channel",
                "concentration_risk_level": self._risk_level(score if key_account >= 55 else max(score - 2, 0)),
                "key_account_dependency": {"percent_of_growth": key_account, "risk": key_account >= 55},
                "channel_trade_risk": {"sell_in_sell_out_gap": sell_gap, "gap_percent": round(sell_gap_percent, 1)},
                "sell_in_vs_sell_out_visibility": "clear_gap_visible" if sell_gap_percent >= 8 else "limited_gap",
                "trade_loading_risk": severity if sell_gap_percent >= 8 else "low",
                "sustainability_judgment": "fragile_or_worse" if score >= 4 else "broadly_sustainable",
                "confidence": confidence,
                "handoff_note": "Concentration and sell-in/sell-out signals evaluated from submitted fields.",
            },
            "agent_3": {
                "margin_impact": {
                    "baseline_margin": margin_before,
                    "promo_margin": margin_during,
                    "erosion_points": round(margin_erosion, 1),
                },
                "trade_spend_efficiency": round(spend_per_incremental_unit, 2),
                "financial_risk_level": self._risk_level(score if margin_erosion >= 8 else max(score - 2, 0)),
                "discount_dependency_risk": "high" if discount >= 20 else "moderate" if discount >= 12 else "low",
                "financial_sustainability_judgment": sustainability,
                "confidence": confidence,
                "handoff_note": "Margin erosion and spend per incremental unit are the main financial signals.",
            },
            "agent_4": {
                "demand_movement": {
                    "uplift_percent": round(uplift, 1),
                    "post_promotion_delta_vs_baseline": round(post_delta, 1),
                    "true_demand_signal": "below_baseline" if post_delta < 0 else "above_baseline",
                },
                "inventory_impact": {
                    "sell_in_sell_out_gap": sell_gap,
                    "gap_percent": round(sell_gap_percent, 1),
                },
                "propagation_risk_level": self._risk_level(score if sell_gap_percent >= 8 else max(score - 3, 0)),
                "post_promotion_behavior": "demand_cliff" if post_delta <= -10 else "stable_or_positive",
                "root_cause_confidence": "high" if data_quality >= 80 else "medium",
                "confidence": confidence,
                "handoff_note": "Inventory buildup and post-promotion behavior indicate whether growth is real demand.",
            },
            "agent_5": {
                "overall_case_severity": severity,
                "urgency": "critical" if score >= 11 else "urgent" if score >= 7 else "elevated" if score >= 4 else "routine",
                "recommended_escalation_level": "CFO_and_VP_Sales" if score >= 11 else "VP_Marketing" if score >= 7 else "Brand_Manager",
                "primary_owner": "Revenue Growth Management",
                "supporting_owners": ["Sales", "Finance", "Supply Chain"],
                "recommended_governance_action": "escalate_and_reassess" if score >= 7 else "monitor_with_controls",
                "reassessment_timing": "within_1_week" if score >= 7 else "within_4_weeks",
                "executive_attention_filter": "yes" if score >= 7 else "watchlist",
                "governance_risk_flags": [
                    flag for flag, active in {
                        "account_concentration": key_account >= 55,
                        "trade_loading": sell_gap_percent >= 20,
                        "margin_erosion": margin_erosion >= 8,
                        "post_promotion_decline": post_delta < 0,
                    }.items() if active
                ],
                "handoff_to_final_brain": "Governance severity is driven by concentration, inventory gap, margin erosion, and post-promotion demand.",
            },
        }

        drivers = [
            f"Key account contribution is {key_account:.1f}%.",
            f"Sell-in exceeds sell-out by {sell_gap:,.0f} units ({sell_gap_percent:.1f}%).",
            f"Post-promotion demand is {post_delta:.1f}% versus baseline.",
            f"Margin erosion is {margin_erosion:.1f} points during promotion.",
            f"Forecast variance is {forecast_variance:.1f}%.",
        ]

        agents["agent_6"] = {
            "growth_health": growth_health,
            "distortion_severity": severity if severity != "medium" else "moderate",
            "strategic_sustainability": sustainability,
            "recommended_action": recommended_action,
            "confidence": confidence,
            "executive_interpretation": (
                f"The promotion generated {uplift:.1f}% uplift, but the decision should be judged through "
                f"concentration, sell-out conversion, margin erosion, and post-promotion demand. "
                f"The rule-based verdict is {growth_health.upper()} with {severity} risk."
            ),
            "strongest_judgment_drivers": drivers,
            "what_leadership_should_not_assume": [
                "Do not assume uplift alone proves real consumer demand.",
                "Do not assume sell-in volume will convert to sustainable sell-out.",
                "Do not repeat the mechanic without validating margin and account concentration.",
            ],
            "required_next_action": recommended_action,
            "owner": "Revenue Growth Management + Sales + Finance",
            "timing": "within 1 week" if score >= 7 else "within 4 weeks",
            "executive_risk_flags": agents["agent_5"]["governance_risk_flags"],
        }

        for number in range(1, 7):
            key = f"agent_{number}"
            self.audit_log.append({
                "id": str(uuid.uuid4()),
                "agent_number": number,
                "agent_name": f"Fallback Agent {number}",
                "timestamp": datetime.utcnow().isoformat(),
                "raw_input": "Rule-based fallback inputs derived from case metrics.",
                "raw_output": json.dumps(agents[key]),
                "parsed_output": agents[key],
                "confidence": agents[key].get("confidence"),
                "error_message": None if number > 1 else reason,
            })

        return {
            "case_id": case_data.get("case_id", str(uuid.uuid4())),
            "agents": agents,
            "errors": [f"Used rule-based fallback: {reason}"],
            "timestamp": datetime.utcnow().isoformat(),
            "final_output": agents["agent_6"],
            "audit_log": self.audit_log,
        }
    
    def run_agent(self, agent_number: int, agent_name: str, system_prompt: str, 
                  user_prompt: str, parser_func) -> tuple[Any, Optional[str]]:
        """
        Run a single agent and handle errors gracefully.
        Returns: (parsed_output, error_message)
        """
        audit_entry = {
            "id": str(uuid.uuid4()),
            "agent_number": agent_number,
            "agent_name": agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "raw_input": user_prompt[:500],  # Store first 500 chars for audit
        }
        
        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
            )
            
            raw_output = response.choices[0].message.content
            audit_entry["raw_output"] = raw_output
            
            # Parse response
            parsed_output = parser_func(raw_output)
            audit_entry["parsed_output"] = parsed_output.dict()
            audit_entry["confidence"] = parsed_output.confidence
            audit_entry["error_message"] = None
            
            self.audit_log.append(audit_entry)
            return parsed_output, None
            
        except Exception as e:
            error_msg = f"Agent {agent_number} ({agent_name}) failed: {str(e)}"
            audit_entry["error_message"] = error_msg
            self.audit_log.append(audit_entry)
            return None, error_msg
    
    def orchestrate(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the full agent workflow sequentially.
        """
        self.audit_log = []
        if not self.client:
            return self._rule_based_analysis(case_data, "OPENAI_API_KEY is not configured")

        results = {
            "case_id": case_data.get("case_id", str(uuid.uuid4())),
            "agents": {},
            "errors": [],
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        # Agent 1: Intent Analysis
        print(f"[Agent 1] Analyzing campaign intent...")
        agent_1_prompt = create_agent_1_prompt(case_data)
        from agents.agent_1_intent import AGENT_1_SYSTEM_PROMPT
        agent_1_output, error = self.run_agent(
            1, "Campaign Intent Analyst", AGENT_1_SYSTEM_PROMPT, agent_1_prompt, parse_agent_1_response
        )
        if error:
            results["errors"].append(error)
            agent_1_output = None
        else:
            results["agents"]["agent_1"] = agent_1_output.dict()
            print(f"[Agent 1] Complete. Intent: {agent_1_output.campaign_intent}")
        
        # Agent 2: Concentration Risk
        if agent_1_output:
            print(f"[Agent 2] Analyzing trade concentration...")
            agent_2_prompt = create_agent_2_prompt(case_data, agent_1_output.dict())
            from agents.agent_2_concentration import AGENT_2_SYSTEM_PROMPT
            agent_2_output, error = self.run_agent(
                2, "Concentration Analyst", AGENT_2_SYSTEM_PROMPT, agent_2_prompt, parse_agent_2_response
            )
            if error:
                results["errors"].append(error)
                agent_2_output = None
            else:
                results["agents"]["agent_2"] = agent_2_output.dict()
                print(f"[Agent 2] Complete. Concentration Risk: {agent_2_output.concentration_risk_level}")
        else:
            agent_2_output = None
            results["errors"].append("Skipping Agent 2 due to Agent 1 failure")
        
        # Agent 3: Margin & Financial
        if agent_1_output and agent_2_output:
            print(f"[Agent 3] Analyzing financial impact...")
            agent_3_prompt = create_agent_3_prompt(case_data, agent_1_output.dict(), agent_2_output.dict())
            from agents.agent_3_margin import AGENT_3_SYSTEM_PROMPT
            agent_3_output, error = self.run_agent(
                3, "Margin Analyst", AGENT_3_SYSTEM_PROMPT, agent_3_prompt, parse_agent_3_response
            )
            if error:
                results["errors"].append(error)
                agent_3_output = None
            else:
                results["agents"]["agent_3"] = agent_3_output.dict()
                print(f"[Agent 3] Complete. Financial Risk: {agent_3_output.financial_risk_level}")
        else:
            agent_3_output = None
            results["errors"].append("Skipping Agent 3 due to prior failures")
        
        # Agent 4: Demand & Inventory
        if agent_1_output and agent_2_output and agent_3_output:
            print(f"[Agent 4] Analyzing demand signals...")
            agent_4_prompt = create_agent_4_prompt(
                case_data, agent_1_output.dict(), agent_2_output.dict(), agent_3_output.dict()
            )
            from agents.agent_4_demand import AGENT_4_SYSTEM_PROMPT
            agent_4_output, error = self.run_agent(
                4, "Demand Analyst", AGENT_4_SYSTEM_PROMPT, agent_4_prompt, parse_agent_4_response
            )
            if error:
                results["errors"].append(error)
                agent_4_output = None
            else:
                results["agents"]["agent_4"] = agent_4_output.dict()
                print(f"[Agent 4] Complete. Propagation Risk: {agent_4_output.propagation_risk_level}")
        else:
            agent_4_output = None
            results["errors"].append("Skipping Agent 4 due to prior failures")
        
        # Agent 5: Governance & Escalation
        if agent_1_output and agent_2_output and agent_3_output and agent_4_output:
            print(f"[Agent 5] Determining governance actions...")
            agent_5_prompt = create_agent_5_prompt(
                case_data, agent_1_output.dict(), agent_2_output.dict(), 
                agent_3_output.dict(), agent_4_output.dict()
            )
            from agents.agent_5_governance import AGENT_5_SYSTEM_PROMPT
            agent_5_output, error = self.run_agent(
                5, "Governance Analyst", AGENT_5_SYSTEM_PROMPT, agent_5_prompt, parse_agent_5_response
            )
            if error:
                results["errors"].append(error)
                agent_5_output = None
            else:
                results["agents"]["agent_5"] = agent_5_output.dict()
                print(f"[Agent 5] Complete. Severity: {agent_5_output.overall_case_severity}")
        else:
            agent_5_output = None
            results["errors"].append("Skipping Agent 5 due to prior failures")
        
        # Agent 6: Executive Brain
        if agent_1_output and agent_2_output and agent_3_output and agent_4_output and agent_5_output:
            print(f"[Agent 6] Producing executive judgment...")
            agent_6_prompt = create_agent_6_prompt(
                case_data, agent_1_output.dict(), agent_2_output.dict(),
                agent_3_output.dict(), agent_4_output.dict(), agent_5_output.dict()
            )
            from agents.agent_6_brain import AGENT_6_SYSTEM_PROMPT
            agent_6_output, error = self.run_agent(
                6, "Executive Brain", AGENT_6_SYSTEM_PROMPT, agent_6_prompt, parse_agent_6_response
            )
            if error:
                results["errors"].append(error)
                agent_6_output = None
            else:
                results["agents"]["agent_6"] = agent_6_output.dict()
                print(f"[Agent 6] Complete. Growth Health: {agent_6_output.growth_health}")
        else:
            agent_6_output = None
            results["errors"].append("Skipping Agent 6 due to prior failures")
        
        if not agent_6_output and results["errors"]:
            return self._rule_based_analysis(case_data, "; ".join(results["errors"]))

        results["final_output"] = agent_6_output.dict() if agent_6_output else None
        results["audit_log"] = self.audit_log
        
        return results
