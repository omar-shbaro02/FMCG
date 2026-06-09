"""
Agent 1: Campaign Intent & Commercial Context Analyst
Evaluates the underlying commercial intent and context of the promotion.
"""

import json
from typing import Dict, Any
from schemas.schemas import Agent1Output


AGENT_1_SYSTEM_PROMPT = """You are Agent 1: Campaign Intent & Commercial Context Analyst for an FMCG Trade Promotion Analysis system.

Your role is to analyze the commercial intent and strategic context behind a trade promotion.

You must evaluate:
1. What is the genuine commercial objective behind this promotion?
2. Is this a volume-drive, market-share grab, seasonal, competitor-response, or inventory-clearing promotion?
3. What is the risk tolerance implied by the promotion design?
4. Are there any red flags in how the promotion has been framed or positioned?
5. Is the intent clear or is there ambiguity that suggests multiple agendas?

You receive the complete promotion case data including sales figures, margins, and management notes.

Output your analysis as a JSON object with these EXACT fields:
{
  "campaign_intent": "string - one sentence statement of the core commercial intent",
  "evaluation_lens": "string - the lens through which you evaluate this (e.g., 'volume growth', 'market defense', 'trade loading')",
  "risk_tolerance": "string - low/medium/high/extreme - what risk level does this design imply the business is willing to accept?",
  "commercial_context_flags": ["array of strings - flags about context, e.g., 'seasonal pressure', 'competitor activity', 'inventory buildup'"],
  "intent_clarity": "string - is the intent clear or ambiguous?",
  "confidence": "float between 0 and 1 - your confidence in this assessment",
  "handoff_note": "string - key insights for the next analyst"
}

Be precise. Do not invent data. If data is missing, acknowledge it in your handoff note.
"""


def create_agent_1_prompt(case_data: Dict[str, Any]) -> str:
    """Create the specific prompt for Agent 1 with case data."""
    
    prompt = f"""{AGENT_1_SYSTEM_PROMPT}

Here is the promotion case to analyze:

PROMOTION CASE DATA:
-------------------
Promotion ID: {case_data.get('promotion_id', 'N/A')}
Brand: {case_data.get('brand', 'N/A')}
Category: {case_data.get('category', 'N/A')}
SKU: {case_data.get('sku', 'N/A')}
Channel: {case_data.get('channel', 'N/A')}
Key Account: {case_data.get('key_account', 'N/A')}
Region: {case_data.get('region', 'N/A')}
Promotion Period: {case_data.get('promotion_period_start', 'N/A')} to {case_data.get('promotion_period_end', 'N/A')}

Campaign Objective (stated): {case_data.get('campaign_objective', 'N/A')}
Promotion Type: {case_data.get('promotion_type', 'N/A')}

SALES METRICS:
- Baseline Sales Volume: {case_data.get('baseline_sales_volume', 'N/A')} units
- Promotion Sales Volume: {case_data.get('promotion_sales_volume', 'N/A')} units
- Uplift %: {case_data.get('uplift_percent', 'N/A')}%
- Key Account Contribution: {case_data.get('key_account_contribution_percent', 'N/A')}%
- Channel Contribution: {case_data.get('channel_contribution_percent', 'N/A')}%

PROMOTION MECHANICS:
- Discount %: {case_data.get('discount_percent', 'N/A')}%
- Trade Spend: ${case_data.get('trade_spend', 'N/A')}
- Number of Participating Customers/Stores: {case_data.get('num_participating_customers', 'N/A')}

FINANCIAL IMPACT:
- Gross Margin Before: {case_data.get('gross_margin_before', 'N/A')}%
- Gross Margin During: {case_data.get('gross_margin_during', 'N/A')}%

MANAGEMENT NOTES:
{case_data.get('management_notes', 'No notes provided')}

DATA QUALITY CONFIDENCE: {case_data.get('data_quality_confidence', 'N/A')}%

-------------------

Now analyze this promotion and provide your assessment in valid JSON format.
Your output MUST be valid JSON. Do not include any text outside the JSON object.
"""
    return prompt


def parse_agent_1_response(raw_response: str) -> Agent1Output:
    """Parse the raw LLM response into Agent1Output schema."""
    try:
        # Extract JSON from the response
        data = json.loads(raw_response)
        return Agent1Output(**data)
    except json.JSONDecodeError:
        # Try to extract JSON from the response if it's embedded in text
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return Agent1Output(**data)
        raise ValueError(f"Could not parse Agent 1 response: {raw_response}")
