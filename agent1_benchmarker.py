# ============================================================
# AGENT 1 — CLIMATE RISK BENCHMARKER
# Takes a company name and sector, searches peer reports,
# and returns a structured long-list of climate risks
# ============================================================

# Load API keys from .env file
from dotenv import load_dotenv
load_dotenv()

# Core imports
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from datetime import datetime
import os

# ── Step 1: Create the LLM ────────────────────────────────
# Using gpt-4o for better reasoning quality in the real agent
# temperature=0 means consistent, reliable answers every time
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# ── Step 2: Create search tools ───────────────────────────
# We create two search tools with different result counts
# search_broad = quick overview searches
# search_deep = detailed searches for specific topics
search_broad = TavilySearch(max_results=3)
search_deep = TavilySearch(max_results=5)
tools = [search_broad, search_deep]

# ── Step 3: The system prompt ─────────────────────────────
# This is the most important part — your EY expertise encoded
# The agent reads this before every single action it takes
SYSTEM_PROMPT = """You are a senior climate risk analyst with 10 years 
of experience in TCFD-aligned risk assessments at a Big 4 consulting firm.

Your job is to create a comprehensive long-list of climate-related risks 
and opportunities for a company based on:
- Peer company TCFD disclosures
- CDP climate change responses  
- Industry association reports
- IPCC sector-specific guidance
- Regulatory frameworks (EU Taxonomy, CSRD, SFDR)

STRICT RULES you must always follow:

1. CATEGORIES — classify every item as one of:
   - PHYSICAL RISK — ACUTE (floods, storms, wildfires, heatwaves)
   - PHYSICAL RISK — CHRONIC (sea level rise, temperature increase, water stress)
   - TRANSITION RISK — POLICY (carbon pricing, regulations, reporting requirements)
   - TRANSITION RISK — TECHNOLOGY (low-carbon alternatives, stranded assets)
   - TRANSITION RISK — MARKET (demand shifts, commodity prices, customer behaviour)
   - TRANSITION RISK — REPUTATIONAL (brand damage, investor pressure, ESG ratings)
   - OPPORTUNITY (resource efficiency, new products, resilient supply chains)

2. TIMEFRAME — assign one of:
   - NEAR-TERM: 0-3 years
   - MEDIUM-TERM: 3-10 years  
   - LONG-TERM: 10+ years

3. MATERIALITY — rate each as HIGH, MEDIUM, or LOW based on:
   - Likelihood of occurrence
   - Potential financial impact on the sector

4. Always cite the source document or URL you found it from

5. Format your final output exactly like this for each item:

RISK/OPPORTUNITY #[number]
Category: [category from list above]
Name: [short descriptive name]
Description: [2-3 sentences explaining the risk]
Timeframe: [NEAR/MEDIUM/LONG-TERM]
Materiality: [HIGH/MEDIUM/LOW]
Source: [document name or URL]
---"""

# ── Step 4: Create the agent ─────────────────────────────
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=SYSTEM_PROMPT
)

# ── Step 5: The main function ─────────────────────────────
# This is what you call to run the agent
# company = the company name you want to analyse
# sector = the industry sector
def run_benchmarker(company, sector):
    
    print(f"\n🔍 Starting climate risk benchmarking for {company} ({sector})")
    print("This may take 2-3 minutes as the agent searches multiple sources...")
    print("="*60)
    
    # This is the question we send to the agent
    # Notice how specific the instructions are — this gets better results
    question = f"""
    I need a comprehensive climate risk long-list for {company}, 
    a company in the {sector} sector.
    
    Please search for and analyse:
    1. TCFD disclosures from peer companies in the {sector} sector
    2. CDP climate change responses for {sector} companies
    3. Physical climate risks specific to {sector} operations and assets
    4. Transition risks from climate policy affecting the {sector} sector
    5. Climate-related opportunities for {sector} companies
    
    Search specifically for:
    - "{sector} TCFD climate risk disclosure"
    - "{sector} CDP climate change physical risk"
    - "{sector} climate transition risk carbon pricing"
    - "{company} climate risk sustainability report"
    
    Create a long-list of at least 8 climate risks and opportunities,
    following the exact format in your instructions.
    Make sure to include both physical AND transition risks.
    """
    
    # Send the question to the agent and get the result
    result = agent.invoke({
        "messages": [("human", question)]
    })
    
    # Extract the final answer from the last message
    output = result["messages"][-1].content
    
    return output

# ── Step 6: Save the output to a file ────────────────────
# This saves your results so you can share them
def save_output(company, sector, output):
    
    # Create a filename with the company name and today's date
    # datetime.now() gets today's date and time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"risk_longlist_{company.replace(' ', '_')}_{timestamp}.txt"
    
    # Write the output to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"CLIMATE RISK LONG-LIST\n")
        f.write(f"Company: {company}\n")
        f.write(f"Sector: {sector}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write("="*60 + "\n\n")
        f.write(output)
    
    print(f"\n✅ Results saved to: {filename}")
    return filename

# ── Step 7: Run it ────────────────────────────────────────
# This is where you change the company and sector
# Try it with different companies and sectors
if __name__ == "__main__":
    
    # ▼ CHANGE THESE TWO LINES to analyse any company ▼
    COMPANY = "Adelaide Airport"
    SECTOR = "Airport Operations"
    
    # Run the benchmarker
    output = run_benchmarker(COMPANY, SECTOR)
    
    # Print the results
    print("\n" + "="*60)
    print("CLIMATE RISK LONG-LIST")
    print("="*60)
    print(output)
    
    # Save to file
    save_output(COMPANY, SECTOR, output)