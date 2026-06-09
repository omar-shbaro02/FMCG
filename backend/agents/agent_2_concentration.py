"""
Agent 2: Trade Concentration & Key Account Risk Analyst
Evaluates concentration risk and trade loading behavior.
"""

import json
from typing import Dict, Any
from schemas.schemas import Agent2Output


AGENT_2_SYSTEM_PROMPT = """You are Agent 2: Trade Concentration & Key Account Risk Analyst.

Your role is to evaluate:
1. How concentrated is the promotional growth? Is it driven by one key account, or distributed?
2. What is the key account dependency risk?
3. Is this a classic trade-loading scenario (pushing volume into the trade channel that won't convert to sell-out)?
4. What is the gap between sell-in and sell-out? 
5. What is the sustainability risk based on concentration?

You receive case data and Agent 1's intent analysis.

Output your analysis as a JSON object with these EXACT fields:
{
  "growth_distribution": {"description": "string", "concentration_score": "float 0-1", "concentration_interpretation": "string"},
  "main_concentration_source": "string - which account/channel/customer group is driving growth?",
  "concentration_risk_level": "string - low/medium/high/critical",
  "key_account_dependency": {"accounts_involved": ["array"], "percent_of_growth": "float", "risk_level": "string"},
  "channel_trade_risk": {"channel": "string", "sell_in_volume": "float", "sell_out_volume": "float", "gap_percent": "float", "risk": "string"},
  "sell_in_vs_sell_out_visibility": "string - is there visibility? Is the data reliable?",
  "trade_loading_risk": "string - is this promotion designed to load the trade rather than drive true demand?",
  "sustainability_judgment": "string - will this growth sustain post-promotion?",
  "confidence": "float between 0 and 1",
  "handoff_note": "string - key insights for Agent 3"
}

Be precise. Flag concentration risks clearly.
"""


def create_agent_2_prompt(case_data: Dict[str, Any], agent_1_output: Dict[str, Any]) -> str:
    """Create the specific prompt for Agent 2."""
    
    prompt = f"""{AGENT_2_SYSTEM_PROMPT}

CASE DATA:
---------
Promotion ID: {case_data.get('promotion_id', 'N/A')}
Brand: {case_data.get('brand', 'N/A')}
Category: {case_data.get('category', 'N/A')}
Channel: {case_data.get('channel', 'N/A')}
Key Account: {case_data.get('key_account', 'N/A')}
Region: {case_data.get('region', 'N/A')}

SALES METRICS:
- Baseline Sales Volume: {case_data.get('baseline_sales_volume', 'N/A')} units
- Promotion Sales Volume: {case_data.get('promotion_sales_volume', 'N/A')} units
- Uplift %: {case_data.get('uplift_percent', 'N/A')}%

CONCENTRATION INDICATORS:
- Key Account Contribution %: {case_data.get('key_account_contribution_percent', 'N/A')}%
- Channel Contribution %: {case_data.get('channel_contribution_percent', 'N/A')}%
- Number of Participating Customers/Stores: {case_data.get('num_participating_customers', 'N/A')}

INVENTORY & FLOW:
- Sell-In Volume: {case_data.get('sell_in_volume', 'N/A')} units
- Sell-Out Volume: {case_data.get('sell_out_volume', 'N/A')} units
- Post-Promotion Demand: {case_data.get('post_promotion_demand', 'N/A')}
- Repeat Order Behavior: {json.dumps(case_data.get('repeat_order_behavior', {}), indent=2)}
- Inventory Impact: {json.dumps(case_data.get('inventory_impact', {}), indent=2)}

AGENT 1 CONTEXT (Campaign Intent Analysis):
-------------------------------------------
Campaign Intent: {agent_1_output.get('campaign_intent', 'N/A')}
Evaluation Lens: {agent_1_output.get('evaluation_lens', 'N/A')}
Risk Tolerance: {agent_1_output.get('risk_tolerance', 'N/A')}
Flags: {json.dumps(agent_1_output.get('commercial_context_flags', []), indent=2)}

-------------------

Analyze the concentration and trade loading risks. Output valid JSON only.
"""
    return prompt


def parse_agent_2_response(raw_response: str) -> Agent2Output:
    """Parse the raw LLM response into Agent2Output schema."""
    try:
        data = json.loads(raw_response)
        return Agent2Output(**data)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return Agent2Output(**data)
        raise ValueError(f"Could not parse Agent 2 response: {raw_response}")
