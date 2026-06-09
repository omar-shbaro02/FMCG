"""
Agent 3: Margin & Trade Efficiency Analyst
Evaluates financial sustainability and efficiency.
"""

import json
from typing import Dict, Any
from schemas.schemas import Agent3Output


AGENT_3_SYSTEM_PROMPT = """You are Agent 3: Margin & Trade Efficiency Analyst.

Your role is to evaluate:
1. What is the true financial impact of this promotion?
2. Is the margin erosion acceptable given the volume uplift?
3. Is the trade spend justified by the incremental volume?
4. What is the discount dependency risk? Can growth be sustained without the discount?
5. Is this promotion financially sustainable long-term?

You receive case data, Agent 1's intent, and Agent 2's concentration analysis.

Output your analysis as a JSON object with these EXACT fields:
{
  "margin_impact": {
    "baseline_gross_margin": "float",
    "promotion_gross_margin": "float",
    "margin_erosion_points": "float - in percentage points",
    "margin_erosion_percent": "float - percent change",
    "total_margin_impact_currency": "float - total margin impact in currency units"
  },
  "trade_spend_efficiency": "float - sales uplift / trade spend ratio",
  "financial_risk_level": "string - low/medium/high/critical",
  "discount_dependency_risk": "string - how dependent is the uplift on the discount? Can it be sustained?",
  "financial_sustainability_judgment": "string - is this financially sustainable?",
  "confidence": "float between 0 and 1",
  "handoff_note": "string - key financial risks for Agent 4"
}

Be precise with calculations. Do not invent missing data.
"""


def create_agent_3_prompt(case_data: Dict[str, Any], agent_1_output: Dict[str, Any], 
                         agent_2_output: Dict[str, Any]) -> str:
    """Create the specific prompt for Agent 3."""
    
    # Calculate some metrics for context
    try:
        baseline_vol = float(case_data.get('baseline_sales_volume', 0))
        promo_vol = float(case_data.get('promotion_sales_volume', 0))
        uplift_vol = promo_vol - baseline_vol
        trade_spend = float(case_data.get('trade_spend', 0))
        
        if trade_spend > 0:
            spend_per_uplift_unit = trade_spend / uplift_vol if uplift_vol > 0 else 0
        else:
            spend_per_uplift_unit = 0
    except:
        spend_per_uplift_unit = 0
    
    prompt = f"""{AGENT_3_SYSTEM_PROMPT}

CASE DATA:
---------
Promotion ID: {case_data.get('promotion_id', 'N/A')}
Brand: {case_data.get('brand', 'N/A')}
Category: {case_data.get('category', 'N/A')}

SALES METRICS:
- Baseline Sales Volume: {case_data.get('baseline_sales_volume', 'N/A')} units
- Promotion Sales Volume: {case_data.get('promotion_sales_volume', 'N/A')} units
- Volume Uplift: {case_data.get('promotion_sales_volume', 0) - case_data.get('baseline_sales_volume', 0)} units

FINANCIAL METRICS:
- Discount %: {case_data.get('discount_percent', 'N/A')}%
- Trade Spend: ${case_data.get('trade_spend', 'N/A')}
- Gross Margin Before Promotion: {case_data.get('gross_margin_before', 'N/A')}%
- Gross Margin During Promotion: {case_data.get('gross_margin_during', 'N/A')}%
- Trade Spend per Uplift Unit: ${spend_per_uplift_unit:.2f}

CONTEXT FROM AGENT 1:
- Campaign Intent: {agent_1_output.get('campaign_intent', 'N/A')}
- Risk Tolerance: {agent_1_output.get('risk_tolerance', 'N/A')}

CONTEXT FROM AGENT 2:
- Concentration Risk Level: {agent_2_output.get('concentration_risk_level', 'N/A')}
- Trade Loading Risk: {agent_2_output.get('trade_loading_risk', 'N/A')}
- Sustainability Judgment: {agent_2_output.get('sustainability_judgment', 'N/A')}

-------------------

Analyze the financial impact and sustainability. Output valid JSON only.
"""
    return prompt


def parse_agent_3_response(raw_response: str) -> Agent3Output:
    """Parse the raw LLM response into Agent3Output schema."""
    try:
        data = json.loads(raw_response)
        return Agent3Output(**data)
    except json.JSONDecodeError:
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return Agent3Output(**data)
        raise ValueError(f"Could not parse Agent 3 response: {raw_response}")
