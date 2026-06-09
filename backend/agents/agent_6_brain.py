"""
Agent 6: Executive Distortion Intelligence Brain
Produces the final leadership judgment on promotional health.
"""

import json
from typing import Dict, Any
from schemas.schemas import Agent6Output


AGENT_6_SYSTEM_PROMPT = """You are Agent 6: Executive Distortion Intelligence Brain.

Your role is to produce ONE clear, defensible leadership judgment about this promotion:
Is the promotional growth HEALTHY, FRAGILE, DISTORTIONARY, or MISLEADING?

This is NOT a summary. This is a JUDGMENT.

You synthesize all 5 specialist agents and the original case data to make a clear, 
confidence-backed recommendation for executive decision-making.

Your judgment must address:
1. Is the growth REAL (true demand increase) or ARTIFICIAL (inventory buildup, trade loading)?
2. Is it SUSTAINABLE post-promotion or FRAGILE?
3. Does it DISTORT the market in ways that damage long-term brand health?
4. Is leadership being MISLED by these numbers?

Output your judgment as a JSON object with these EXACT fields:
{
  "growth_health": "string - HEALTHY / FRAGILE / DISTORTIONARY / MISLEADING",
  "distortion_severity": "string - none / low / moderate / high / critical",
  "strategic_sustainability": "string - sustainable / at_risk / unsustainable",
  "recommended_action": "string - clear, actionable recommendation for leadership",
  "confidence": "float between 0 and 1 - your confidence in this judgment",
  "executive_interpretation": "string - one paragraph for CEO/CFO to understand this in business terms",
  "strongest_judgment_drivers": ["array - top 3-5 reasons supporting this judgment"],
  "what_leadership_should_not_assume": ["array - critical assumptions to avoid"],
  "required_next_action": "string - what must happen next?",
  "owner": "string - who owns the next action?",
  "timing": "string - when should this action happen?",
  "executive_risk_flags": ["array - risks that could change this judgment"]
}

Be definitive. Use the EXACT terminology provided (HEALTHY, FRAGILE, DISTORTIONARY, MISLEADING).
Do not hedge. Make a judgment.
"""


def create_agent_6_prompt(case_data: Dict[str, Any], 
                         agent_1_output: Dict[str, Any],
                         agent_2_output: Dict[str, Any],
                         agent_3_output: Dict[str, Any],
                         agent_4_output: Dict[str, Any],
                         agent_5_output: Dict[str, Any]) -> str:
    """Create the specific prompt for Agent 6."""
    
    prompt = f"""{AGENT_6_SYSTEM_PROMPT}

ORIGINAL CASE:
--------------
Promotion ID: {case_data.get('promotion_id', 'N/A')}
Brand: {case_data.get('brand', 'N/A')}
Category: {case_data.get('category', 'N/A')}
SKU: {case_data.get('sku', 'N/A')}
Channel: {case_data.get('channel', 'N/A')}
Region: {case_data.get('region', 'N/A')}
Campaign Objective: {case_data.get('campaign_objective', 'N/A')}

KEY NUMBERS:
- Baseline: {case_data.get('baseline_sales_volume', 'N/A')} units
- Promotion: {case_data.get('promotion_sales_volume', 'N/A')} units
- Uplift: {case_data.get('uplift_percent', 'N/A')}%
- Margin: {case_data.get('gross_margin_before', 'N/A')}% → {case_data.get('gross_margin_during', 'N/A')}%
- Trade Spend: ${case_data.get('trade_spend', 'N/A')}
- Key Account %: {case_data.get('key_account_contribution_percent', 'N/A')}%
- Sell-In: {case_data.get('sell_in_volume', 'N/A')} units
- Sell-Out: {case_data.get('sell_out_volume', 'N/A')} units

AGENT 1 - INTENT ANALYSIS:
Intent: {agent_1_output.get('campaign_intent', 'N/A')}
Clarity: {agent_1_output.get('intent_clarity', 'N/A')}
Risk Tolerance: {agent_1_output.get('risk_tolerance', 'N/A')}
Confidence: {agent_1_output.get('confidence', 'N/A')}

AGENT 2 - CONCENTRATION:
Main Source: {agent_2_output.get('main_concentration_source', 'N/A')}
Concentration Risk: {agent_2_output.get('concentration_risk_level', 'N/A')}
Trade Loading Risk: {agent_2_output.get('trade_loading_risk', 'N/A')}
Sustainability: {agent_2_output.get('sustainability_judgment', 'N/A')}
Confidence: {agent_2_output.get('confidence', 'N/A')}

AGENT 3 - FINANCIAL:
Risk Level: {agent_3_output.get('financial_risk_level', 'N/A')}
Trade Spend Efficiency: {agent_3_output.get('trade_spend_efficiency', 'N/A')}
Sustainability: {agent_3_output.get('financial_sustainability_judgment', 'N/A')}
Confidence: {agent_3_output.get('confidence', 'N/A')}

AGENT 4 - DEMAND:
Propagation Risk: {agent_4_output.get('propagation_risk_level', 'N/A')}
Post-Promotion Behavior: {agent_4_output.get('post_promotion_behavior', 'N/A')}
Root Cause Confidence: {agent_4_output.get('root_cause_confidence', 'N/A')}
Confidence: {agent_4_output.get('confidence', 'N/A')}

AGENT 5 - GOVERNANCE:
Overall Severity: {agent_5_output.get('overall_case_severity', 'N/A')}
Urgency: {agent_5_output.get('urgency', 'N/A')}
Escalation Level: {agent_5_output.get('recommended_escalation_level', 'N/A')}
Executive Attention: {agent_5_output.get('executive_attention_filter', 'N/A')}

DATA QUALITY: {case_data.get('data_quality_confidence', 'N/A')}%

-------------------

Now make your FINAL JUDGMENT on this promotion's health and sustainability.
Output valid JSON only. Be definitive.
"""
    return prompt


def parse_agent_6_response(raw_response: str) -> Agent6Output:
    """Parse the raw LLM response into Agent6Output schema."""
    try:
        data = json.loads(raw_response)
        return Agent6Output(**data)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return Agent6Output(**data)
        raise ValueError(f"Could not parse Agent 6 response: {raw_response}")
