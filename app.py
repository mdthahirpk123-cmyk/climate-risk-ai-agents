# ============================================================
# CLIMATE RISK BENCHMARKER — STREAMLIT UI (Version 4)
# Enhanced with Geography, Value Chain, and Reporting Framework
# ============================================================

import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.prebuilt import create_react_agent
from datetime import datetime

# Load API keys
load_dotenv()

# ── Page configuration ────────────────────────────────────
st.set_page_config(
    page_title="Climate Risk Benchmarker",
    page_icon="🌍",
    layout="wide"
)

# ── Page header ───────────────────────────────────────────
st.title("🌍 Climate Risk Benchmarker")
st.markdown("**Powered by AI** — searches peer TCFD reports, CDP disclosures, and sustainability reports to generate a climate risk long-list for any company.")
st.caption("* Required fields")
st.divider()

# ── Mandatory inputs ──────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    company = st.text_input(
        "Company Name *",
        placeholder="e.g. Adelaide Airport, Tata Steel, IKEA"
    )

with col2:
    sector = st.text_input(
        "Sector / Industry *",
        placeholder="e.g. Airport Operations, Steel Manufacturing, Retail"
    )

# ── Geography ─────────────────────────────────────────────
geography = st.text_input(
    "Geography (optional)",
    placeholder="e.g. India, Australia, GCC, Global Operations"
)

# ── Value Chain Scope ─────────────────────────────────────
st.markdown("**Value Chain Scope** (optional)")
st.caption("Select which parts of the value chain to include in the analysis")

col_vc1, col_vc2, col_vc3 = st.columns([1, 1, 1])

with col_vc1:
    upstream = st.checkbox("Upstream", value=True)
with col_vc2:
    own_operations = st.checkbox("Own Operations", value=True)
with col_vc3:
    downstream = st.checkbox("Downstream", value=True)

st.divider()

# ── Reporting Framework ───────────────────────────────────
# Each framework has a name and a description of how it
# changes the agent's analysis approach
st.markdown("**Reporting Framework** (optional)")
st.caption("Select one or more frameworks to align the output to. Leave blank for a general TCFD-aligned output.")

# Framework definitions
# Each entry: display name, short description shown to user,
# and instructions sent to the agent
FRAMEWORKS = {
    "TCFD": {
        "label": "TCFD",
        "description": "Task Force on Climate-related Financial Disclosures",
        "instruction": """Align the output to the TCFD framework. 
        Use TCFD's four pillars: Governance, Strategy, Risk Management, 
        and Metrics & Targets. Classify risks under TCFD categories of 
        physical risks (acute and chronic) and transition risks 
        (policy, legal, technology, market, reputational)."""
    },
    "CSRD": {
        "label": "CSRD / ESRS",
        "description": "European Sustainability Reporting Standards",
        "instruction": """Align the output to CSRD and ESRS E1 (Climate Change). 
        Apply double materiality — assess both financial materiality 
        (how climate affects the company) and impact materiality 
        (how the company affects the climate). Use ESRS E1 disclosure 
        requirements including transition plan, physical risks, 
        and climate-related targets."""
    },
    "BRSR": {
        "label": "BRSR",
        "description": "Business Responsibility and Sustainability Report (India)",
        "instruction": """Align the output to BRSR (SEBI). 
        Focus on India-specific climate risks and regulatory requirements. 
        Use BRSR's prescribed categories for environmental risks. 
        Include risks relevant to Indian regulatory context — 
        Bureau of Energy Efficiency, CPCB regulations, 
        India's NDC commitments, and PAT scheme."""
    },
    "CDP": {
        "label": "CDP",
        "description": "CDP Climate Change Questionnaire",
        "instruction": """Align the output to CDP Climate Change disclosure requirements. 
        Structure risks using CDP's risk categories and time horizons. 
        Include financial impact quantification where possible. 
        Reference CDP scoring methodology and sector-specific 
        guidance notes."""
    },
    "GRI": {
        "label": "GRI Standards",
        "description": "Global Reporting Initiative",
        "instruction": """Align the output to GRI Standards — specifically 
        GRI 201 (Economic Performance), GRI 302 (Energy), 
        GRI 303 (Water), and GRI 305 (Emissions). 
        Focus on material topics and stakeholder relevance. 
        Include both risks and opportunities framed around 
        GRI's materiality assessment approach."""
    },
    "ISSB": {
        "label": "ISSB / IFRS S2",
        "description": "International Sustainability Standards Board",
        "instruction": """Align the output to IFRS S2 Climate-related Disclosures. 
        Focus on climate-related risks and opportunities that could 
        reasonably be expected to affect the entity's cash flows, 
        access to finance, or cost of capital. Use ISSB's 
        industry-based metrics from SASB standards where relevant."""
    },
    "EU_TAXONOMY": {
        "label": "EU Taxonomy",
        "description": "EU Taxonomy for Sustainable Activities",
        "instruction": """Align the output to EU Taxonomy requirements. 
        Assess which activities substantially contribute to climate 
        change mitigation or adaptation. Identify Do No Significant Harm 
        (DNSH) criteria and minimum social safeguards. 
        Flag transition and enabling activities relevant to the sector."""
    },
    "SFDR": {
        "label": "SFDR",
        "description": "Sustainable Finance Disclosure Regulation",
        "instruction": """Align the output to SFDR Principal Adverse Impact (PAI) indicators. 
        Focus on climate and environment-related PAIs including 
        GHG emissions, carbon footprint, fossil fuel exposure, 
        and biodiversity risks. Frame risks from an 
        investor and financial product perspective."""
    }
}

# Display frameworks in a 4-column grid
# This makes it look clean and organised on the page
fw_col1, fw_col2, fw_col3, fw_col4 = st.columns(4)
fw_columns = [fw_col1, fw_col2, fw_col3, fw_col4]

selected_frameworks = []

for i, (key, fw) in enumerate(FRAMEWORKS.items()):
    with fw_columns[i % 4]:
        if st.checkbox(
            fw["label"],
            help=fw["description"]
        ):
            selected_frameworks.append(key)

st.divider()

# ── Run button ────────────────────────────────────────────
run_button = st.button("🔍 Run Climate Risk Analysis", type="primary")

# ── Agent setup ───────────────────────────────────────────
@st.cache_resource
def setup_agent():
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    search_broad = TavilySearch(max_results=3)
    search_deep = TavilySearch(max_results=5)
    tools = [search_broad, search_deep]

    SYSTEM_PROMPT = """You are a senior climate risk analyst with 10 years 
    of experience in TCFD-aligned risk assessments at a Big 4 consulting firm.

    Your job is to create a comprehensive long-list of climate-related risks 
    and opportunities for a company based on:
    - Peer company TCFD disclosures
    - CDP climate change responses
    - Sustainability and integrated annual reports
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

    3. MATERIALITY — rate each as HIGH, MEDIUM, or LOW

    4. Always cite the source document or URL

    5. Format your final output exactly like this for each item:

    RISK/OPPORTUNITY #[number]
    Category: [category from list above]
    Name: [short descriptive name]
    Description: [2-3 sentences explaining the risk]
    Value Chain Affected: [Upstream / Own Operations / Downstream / Multiple]
    Timeframe: [NEAR/MEDIUM/LONG-TERM]
    Materiality: [HIGH/MEDIUM/LOW]
    Framework Relevance: [which selected frameworks flag this risk]
    Source: [document name or URL]
    ---"""

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )

    return agent

# ── Main logic ────────────────────────────────────────────
if run_button:

    if not company or not sector:
        st.warning("⚠️ Please fill in Company Name and Sector — these are required. All other fields are optional.")

    else:
        agent = setup_agent()

        # ── Build geography context ───────────────────────
        geography_context = f"The company operates in {geography}." if geography else ""
        geography_search = f"in {geography}" if geography else ""
        geography_instruction = f"Pay particular attention to geography-specific physical risks for {geography} such as region-specific hazards, local regulations, and climate patterns." if geography else ""

        # ── Build value chain context ─────────────────────
        selected_value_chain = []
        if upstream:
            selected_value_chain.append("Upstream (raw material sourcing and supply chain)")
        if own_operations:
            selected_value_chain.append("Own Operations (direct assets, facilities, and processes)")
        if downstream:
            selected_value_chain.append("Downstream (products, customers, and end of life)")

        if selected_value_chain:
            value_chain_context = f"Focus the analysis on these value chain stages: {', '.join(selected_value_chain)}."
            value_chain_instruction = f"For each risk and opportunity, specify which value chain stage is affected — Upstream, Own Operations, or Downstream. Only include risks relevant to these selected value chain stages: {', '.join(selected_value_chain)}."
        else:
            value_chain_context = ""
            value_chain_instruction = ""

        # ── Build framework context ───────────────────────
        if selected_frameworks:
            framework_names = [FRAMEWORKS[f]["label"] for f in selected_frameworks]
            framework_instructions = "\n".join([FRAMEWORKS[f]["instruction"] for f in selected_frameworks])
            framework_context = f"""
            The output must be aligned to these reporting frameworks: {', '.join(framework_names)}.
            
            Framework-specific instructions:
            {framework_instructions}
            
            For each risk and opportunity, include a 'Framework Relevance' field 
            showing which of these frameworks ({', '.join(framework_names)}) 
            specifically flag or require disclosure of this risk.
            """
        else:
            framework_context = "Use general TCFD-aligned categories for the output."

        with st.spinner(f"Analysing climate risks for {company}... this takes 2-3 minutes"):

            question = f"""
            I need a comprehensive climate risk long-list for {company}, 
            a company in the {sector} sector.
            {geography_context}

            Please search for and analyse:
            1. TCFD disclosures from peer companies in the {sector} sector
            2. CDP climate change responses for {sector} companies
            3. Sustainability and annual reports from peer {sector} companies
            4. Physical climate risks specific to {sector} operations {geography_search}
            5. Transition risks from climate policy affecting {sector} {geography_search}
            6. Climate-related opportunities for {sector} companies

            Search specifically for:
            - "{sector} TCFD climate risk disclosure"
            - "{sector} CDP climate change physical risk {geography_search}"
            - "{sector} climate transition risk carbon pricing {geography_search}"
            - "{company} climate risk sustainability report"

            Create a long-list of at least 8 climate risks and opportunities.
            Follow the exact format in your instructions.
            Include both physical AND transition risks.
            {geography_instruction}
            {value_chain_context}
            {value_chain_instruction}
            {framework_context}
            """

            result = agent.invoke({
                "messages": [("human", question)]
            })

            output = result["messages"][-1].content

        # ── Display results ───────────────────────────────
        st.success("✅ Analysis complete!")
        st.divider()

        st.subheader(f"Climate Risk Long-List: {company}")

        # Build metadata caption
        framework_display = ', '.join([FRAMEWORKS[f]["label"] for f in selected_frameworks]) if selected_frameworks else "General TCFD"
        st.caption(f"Sector: {sector} | Geography: {geography if geography else 'Not specified'} | Frameworks: {framework_display} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        st.markdown(output)
        st.divider()

        # ── Download button ───────────────────────────────
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"risk_longlist_{company.replace(' ', '_')}_{timestamp}.txt"

        download_content = f"""CLIMATE RISK LONG-LIST
Company: {company}
Sector: {sector}
Geography: {geography if geography else 'Not specified'}
Value Chain Scope: {', '.join(selected_value_chain) if selected_value_chain else 'Not specified'}
Frameworks: {framework_display}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*60}

{output}"""

        st.download_button(
            label="📥 Download Results as Text File",
            data=download_content,
            file_name=filename,
            mime="text/plain"
        )