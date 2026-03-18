# ruff: noqa
# MarketingTool.pro — Google Ads AI Agent
# Vertex AI + Gemini 3 Pro + Google Search + URL Context + AI Router 8 models

import os
import json
import requests
import google.auth
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import url_context
from google.adk.apps import App

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

AI_ROUTER = os.environ.get("AI_ROUTER_URL", "http://31.220.107.19:9000")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://62.72.58.221:8000")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")


def _ai(task, prompt, t=25):
    try:
        r = requests.post(f"{AI_ROUTER}/generate", json={"task": task, "prompt": prompt}, timeout=t)
        return r.json().get("response", "") if r.status_code == 200 else ""
    except:
        return ""


def _save(table, data):
    if not SUPABASE_KEY: return
    try:
        requests.post(f"{SUPABASE_URL}/rest/v1/{table}",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}",
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            json=data, timeout=10)
    except: pass


def create_campaign(brand: str, url: str, objective: str, budget: float, location: str, industry: str = "general") -> str:
    """Create Google Ads campaign with ad groups, keywords, ads, targeting, projections.
    Args:
        brand: Brand name
        url: Website URL
        objective: search/display/shopping/video/performance_max
        budget: Daily budget dollars
        location: Target location
        industry: Industry niche
    """
    c = _ai("creative", f"Google Ads {objective} campaign for {brand} ({url}). ${budget}/day. {location}. {industry}. 3 ad groups with 5 keywords each, 2 RSAs with 15 headlines 4 descriptions, targeting, projections. No placeholders.", 60)
    r = _ai("research", f"Benchmarks for {brand} in {industry}. CPC, CTR, ROAS.", 15)
    i = _ai("image_gen", f"Google ad banner for {brand}. Modern. No text.", 25)
    _save("automation_logs", {"type": "campaign_create", "config": json.dumps({"brand": brand, "objective": objective}), "status": "active"})
    return json.dumps({"campaign": c, "benchmarks": r, "image": i})


def generate_ads(brand: str, product: str, audience: str, tone: str = "professional") -> str:
    """Generate 15 headlines + 4 descriptions for Google RSAs.
    Args:
        brand: Brand name
        product: Product/service
        audience: Target audience
        tone: professional/casual/urgent/bold
    """
    c = _ai("creative", f"Google RSAs for {brand} — {product}. {audience}. {tone}. 15 headlines 30chars, 4 descriptions 90chars, 3 CTAs.", 30)
    i = _ai("image_gen", f"Ad image for {brand} - {product}. Modern. No text.", 25)
    return json.dumps({"adCopy": c, "image": i})


def research_keywords(topic: str, location: str = "US") -> str:
    """Research 30 keywords with volume, competition, CPC.
    Args:
        topic: Topic to research
        location: Target location
    """
    k = _ai("research", f'Keywords for "{topic}". {location}. 10 high intent, 10 medium, 10 long tail. keyword, searches, competition, CPC.', 20)
    n = _ai("research", f'20 negative keywords for "{topic}".', 12)
    return json.dumps({"keywords": k, "negatives": n})


def optimize_budget(budget: float, campaigns: str, goal: str) -> str:
    """Optimize budget across campaigns.
    Args:
        budget: Monthly budget dollars
        campaigns: Current campaigns
        goal: maximize_conversions/clicks/target_roas/target_cpa
    """
    o = _ai("automation", f"Optimize ${budget}/month. {goal}. {campaigns}. Allocation, strategy, scaling.", 20)
    f = _ai("research", f"30-day forecast ${budget}/month, {goal}. Clicks, conversions, CPA, ROAS.", 12)
    return json.dumps({"optimization": o, "forecast": f})


def audit_account(description: str, spend: float = 0) -> str:
    """Audit Google Ads account.
    Args:
        description: Account description
        spend: Monthly spend
    """
    a = _ai("creative", f"Google Ads audit: {description}. ${spend}/month. Score 0-100, issues, 10 recommendations.", 30)
    b = _ai("research", f"Benchmarks: {description}. CTR, CPC, quality score.", 12)
    _save("insights", {"type": "google_audit", "data": json.dumps({"description": description}), "score": 0})
    return json.dumps({"audit": a, "benchmarks": b})


def analyze_campaign(campaign: str, platform: str, metrics: str = "") -> str:
    """Analyze campaign performance.
    Args:
        campaign: Campaign name
        platform: google/meta/both
        metrics: Current metrics
    """
    a = _ai("research", f'Analyze "{campaign}" {platform}. {metrics}. Assessment, issues.', 20)
    c = _ai("creative", f'5 actions for "{campaign}" {platform}. Change, impact, priority.', 15)
    r = _ai("automation", f'5 rules for "{campaign}". Trigger, action, impact.', 12)
    return json.dumps({"analysis": a, "actions": c, "rules": r})


def generate_landing_page(brand: str, product: str, keyword: str, offer: str = "Free trial") -> str:
    """Generate landing page for quality score.
    Args:
        brand: Brand name
        product: Product
        keyword: Primary keyword
        offer: Offer/CTA
    """
    p = _ai("creative", f'Landing page {brand} — {product}. "{keyword}". {offer}. Hero, benefits, FAQ, CTA, meta.', 30)
    i = _ai("image_gen", f"Landing page hero for {brand} - {product}. Modern. No text.", 25)
    return json.dumps({"page": p, "image": i})


# ══════════════════════════════════════════════════════════════
# SUB-AGENTS
# ══════════════════════════════════════════════════════════════

google_search_agent = LlmAgent(
    name='marketingtool_search_agent',
    model='gemini-3-pro-preview',
    description='Agent for Google searches — market research, competitor analysis, industry benchmarks.',
    sub_agents=[],
    instruction='Use GoogleSearchTool to find real-time market data, competitor ads, industry benchmarks, trending keywords for Google Ads campaigns.',
    tools=[GoogleSearchTool()],
)

url_context_agent = LlmAgent(
    name='marketingtool_url_agent',
    model='gemini-3-pro-preview',
    description='Agent for URL analysis — landing pages, competitor websites, ad destinations.',
    sub_agents=[],
    instruction='Use UrlContextTool to analyze landing pages for quality score, competitor websites, ad destinations.',
    tools=[url_context],
)

# ══════════════════════════════════════════════════════════════
# ROOT AGENT
# ══════════════════════════════════════════════════════════════

root_agent = LlmAgent(
    name='marketingtool_agent',
    model='gemini-3-pro-preview',
    description='MarketingTool.pro Google Ads AI Agent — campaigns, ad copy, keywords, budgets, audits, landing pages, Google Search, URL analysis.',
    sub_agents=[],
    instruction='''You are MarketingTool.pro Google Ads AI Agent.

Tools: create_campaign, generate_ads, research_keywords, optimize_budget, audit_account, analyze_campaign, generate_landing_page, Google Search, URL Context.

Rules: Real specific content. No placeholders. Data-driven. Actionable. Save to Supabase.''',
    tools=[
        create_campaign, generate_ads, research_keywords, optimize_budget,
        audit_account, analyze_campaign, generate_landing_page,
        agent_tool.AgentTool(agent=google_search_agent),
        agent_tool.AgentTool(agent=url_context_agent),
    ],
)

app = App(root_agent=root_agent, name="marketingtool")
