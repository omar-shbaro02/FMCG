"""
Agent 5: Governance & Escalation Analyst
Synthesizes risk signals and recommends governance actions.
"""

import json
from typing import Dict, Any
from schemas.schemas import Agent5Output


AGENT_5_SYSTEM_PROMPT = """You are Agent 5: Governance & Escalation Analyst.

Your role is to:
1. Synthesize the risk signals from Agents 1-4
2. Determine the overall severity and urgency
3. Recommend escalation level and governance actions
4. Identify the right decision-maker and supporting stakeholders
5. Flag governance risks that require executive attention

You receive all prior agent outputs and complete case data.

Output your analysis as a JSON object with these EXACT fields:
{
  "overall_case_severity": "string - low/medium/high/critical",
  "urgency": "string - routine/elevated/urgent/critical",
  "recommended_escalation_level": "string - e.g., 'Category Manager', 'Brand Director', 'VP Marketing', 'CFO'",
  "primary_owner": "string - who should own this decision?",
  "supporting_owners": ["array - other stakeholders who should be involved"],
  "recommended_governance_action": "string - what governance action is recommended?",
  "reassessment_timing": "string - when should this be reassessed?",
  "executive_attention_filter": "string - does this need executive attention?",
  "governance_risk_flags": ["array - governance risks to flag"],
  "handoff_to_final_brain": "string - summary for final judgment"
}

Be clear on severity and escalation.
"""


def create_agent_5_prompt(case_data: Dict[str, Any], agent_1_output: Dict[str, Any],
                         agent_2_output: Dict[str, Any], agent_3_output: Dict[str, Any],
                         agent_4_output: Dict[str, Any]) -> str:
    """Create the specific prompt for Agent 5."""
    
    prompt = f"""{AGENT_5_SYSTEM_PROMPT}

CASE SUMMARY:
-----------
Promotion ID: {case_data.get('promotion_id', 'N/A')}
Brand: {case_data.get('brand', 'N/A')}
Category: {case_data.get('category', 'N/A')}
Channel: {case_data.get('channel', 'N/A')}
Region: {case_data.get('region', 'N/A')}

KEY METRICS:
- Uplift %: {case_data.get('uplift_percent', 'N/A')}%
- Margin Impact: {case_data.get('gross_margin_before', 'N/A')}% → {case_data.get('gross_margin_during', 'N/A')}%
- Trade Spend: ${case_data.get('trade_spend', 'N/A')}

AGENT 1 - INTENT ANALYSIS:
- Intent: {agent_1_output.get('campaign_intent', 'N/A')}
- Intent Clarity: {agent_1_output.get('intent_clarity', 'N/A')}
- Risk Tolerance: {agent_1_output.get('risk_tolerance', 'N/A')}
- Confidence: {agent_1_output.get('confidence', 'N/A')}

AGENT 2 - CONCENTRATION RISK:
- Concentration Risk Level: {agent_2_output.get('concentration_risk_level', 'N/A')}
- Trade Loading Risk: {agent_2_output.get('trade_loading_risk', 'N/A')}
- Sustainability: {agent_2_output.get('sustainability_judgment', 'N/A')}
- Confidence: {agent_2_output.get('confidence', 'N/A')}

AGENT 3 - FINANCIAL RISK:
- Financial Risk Level: {agent_3_output.get('financial_risk_level', 'N/A')}
- Trade Spend Efficiency: {agent_3_output.get('trade_spend_efficiency', 'N/A')}
- Financial Sustainability: {agent_3_output.get('financial_sustainability_judgment', 'N/A')}
- Confidence: {agent_3_output.get('confidence', 'N/A')}

AGENT 4 - DEMAND SIGNALS:
- Propagation Risk Level: {agent_4_output.get('propagation_risk_level', 'N/A')}
- Post-Promotion Behavior: {agent_4_output.get('post_promotion_behavior', 'N/A')}
- Confidence: {agent_4_output.get('confidence', 'N/A')}

RISK SYNTHESIS:
All risk signals indicate overall patterns in intent clarity, concentration, financial health, 
and demand authenticity. Your job is to synthesize these into governance recommendations.

-------------------

Provide governance and escalation recommendations. Output valid JSON only.
"""
    return prompt


def parse_agent_5_response(raw_response: str) -> Agent5Output:
    """Parse the raw LLM response into Agent5Output schema."""
    try:
        data = json.loads(raw_response)
        return Agent5Output(**data)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return Agent5Output(**data)
        raise ValueError(f"Could not parse Agent 5 response: {raw_response}")
