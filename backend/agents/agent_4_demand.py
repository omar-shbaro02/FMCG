"""
Agent 4: Demand & Inventory Propagation Analyst
Evaluates true demand signals and supply chain health.
"""

import json
from typing import Dict, Any
from schemas.schemas import Agent4Output


AGENT_4_SYSTEM_PROMPT = """You are Agent 4: Demand & Inventory Propagation Analyst.

Your role is to evaluate:
1. Is the observed volume growth driven by true demand or artificial inventory buildup?
2. What do post-promotion demand signals tell us about sustainable demand?
3. Is there inventory propagation up the supply chain (bullwhip effect)?
4. What will happen after the promotion ends?
5. Are there replenishment issues or forecast variance problems?

You receive all prior agent outputs and complete case data.

Output your analysis as a JSON object with these EXACT fields:
{
  "demand_movement": {
    "during_promotion": "string - assessment of demand during promotion",
    "post_promotion": "string - assessment of demand after promotion",
    "true_demand_signal": "string - our best assessment of real underlying demand"
  },
  "inventory_impact": {
    "inventory_buildup": "string - is there evidence of inventory buildup?",
    "propagation_risk": "string - is inventory propagating up the supply chain?",
    "replenishment_issues": "string - any issues with replenishment or forecasting?"
  },
  "propagation_risk_level": "string - low/medium/high/critical - risk of bullwhip effect",
  "post_promotion_behavior": "string - what do we expect to happen post-promotion?",
  "root_cause_confidence": "string - confidence in our understanding of what's really driving growth",
  "confidence": "float between 0 and 1",
  "handoff_note": "string - key demand signal issues for Agent 5"
}

Be realistic about what we can and cannot confirm with available data.
"""


def create_agent_4_prompt(case_data: Dict[str, Any], agent_1_output: Dict[str, Any],
                         agent_2_output: Dict[str, Any], agent_3_output: Dict[str, Any]) -> str:
    """Create the specific prompt for Agent 4."""
    
    prompt = f"""{AGENT_4_SYSTEM_PROMPT}

CASE DATA:
---------
Promotion ID: {case_data.get('promotion_id', 'N/A')}
Brand: {case_data.get('brand', 'N/A')}
Category: {case_data.get('category', 'N/A')}

SALES & DEMAND METRICS:
- Baseline Sales Volume: {case_data.get('baseline_sales_volume', 'N/A')} units
- Promotion Sales Volume: {case_data.get('promotion_sales_volume', 'N/A')} units
- Post-Promotion Demand: {case_data.get('post_promotion_demand', 'N/A')}
- Repeat Order Behavior: {json.dumps(case_data.get('repeat_order_behavior', {}), indent=2)}

INVENTORY SIGNALS:
- Sell-In Volume: {case_data.get('sell_in_volume', 'N/A')} units
- Sell-Out Volume: {case_data.get('sell_out_volume', 'N/A')} units
- Inventory Impact: {json.dumps(case_data.get('inventory_impact', {}), indent=2)}
- Replenishment Issues: {case_data.get('replenishment_issues', 'N/A')}
- Forecast Variance: {case_data.get('forecast_variance', 'N/A')}%

PRIOR AGENT INSIGHTS:
- Agent 1 Intent: {agent_1_output.get('campaign_intent', 'N/A')}
- Agent 2 Trade Loading Risk: {agent_2_output.get('trade_loading_risk', 'N/A')}
- Agent 3 Financial Risk: {agent_3_output.get('financial_risk_level', 'N/A')}

DATA QUALITY: {case_data.get('data_quality_confidence', 'N/A')}%

-------------------

Analyze demand signals and inventory propagation. Output valid JSON only.
"""
    return prompt


def parse_agent_4_response(raw_response: str) -> Agent4Output:
    """Parse the raw LLM response into Agent4Output schema."""
    try:
        data = json.loads(raw_response)
        return Agent4Output(**data)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return Agent4Output(**data)
        raise ValueError(f"Could not parse Agent 4 response: {raw_response}")
