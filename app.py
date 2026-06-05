# ============================================================
# CLIMATE RISK BENCHMARKER — STREAMLIT UI
# A web app interface for Agent 1
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
# This sets up the browser tab title and layout
# Must be the first Streamlit command in your file
st.set_page_config(
    page_title="Climate Risk Benchmarker",
    page_icon="🌍",
    layout="wide"
)

# ── Page header ───────────────────────────────────────────
# st.title = big heading
# st.markdown = smaller text, supports formatting
st.title("🌍 Climate Risk Benchmarker")
st.markdown("Searches peer TCFD reports, CDP disclosures, and industry frameworks to generate a climate risk long-list for any company.")

# A horizontal line to separate the header from the content
st.divider()

# ── Input section ─────────────────────────────────────────
# st.columns splits the page into side-by-side sections
# [1, 1] means two equal columns
col1, col2 = st.columns([1, 1])

# Left column — company name input
with col1:
    # st.text_input creates a text box
    # The text inside the brackets is the label shown above the box
    company = st.text_input(
        "Company Name",
        placeholder="e.g. Adelaide Airport, Tata Steel, IKEA"
    )

# Right column — sector input
with col2:
    sector = st.text_input(
        "Sector / Industry",
        placeholder="e.g. Airport Operations, Steel Manufacturing, Retail"
    )

# ── Run button ────────────────────────────────────────────
# st.button creates a clickable button
# When clicked it returns True, otherwise False
run_button = st.button("🔍 Run Climate Risk Analysis", type="primary")

# ── Agent setup ───────────────────────────────────────────
# We use st.cache_resource so the agent is only created once
# Without this, it would recreate the agent every time you click the button
# Think of it like loading a car once instead of rebuilding it every trip
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
    Timeframe: [NEAR/MEDIUM/LONG-TERM]
    Materiality: [HIGH/MEDIUM/LOW]
    Source: [document name or URL]
    ---"""
    
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT
    )
    
    return agent

# ── Main logic — what happens when button is clicked ──────
# This only runs when the button is clicked AND
# both company and sector fields are filled in
if run_button:
    
    # Check if both fields are filled in
    # If either is empty, show a warning instead of running
    if not company or not sector:
        st.warning("⚠️ Please fill in both the Company Name and Sector fields.")
    
    else:
        # Set up the agent
        agent = setup_agent()
        
        # Show a spinner while the agent is working
        # Everything inside this "with" block runs while spinner shows
        with st.spinner(f"Analysing climate risks for {company}... this takes 2-3 minutes"):
            
            # Build the question
            question = f"""
            I need a comprehensive climate risk long-list for {company}, 
            a company in the {sector} sector.
            
            Please search for and analyse:
            1. TCFD disclosures from peer companies in the {sector} sector
            2. CDP climate change responses for {sector} companies
            3. Physical climate risks specific to {sector} operations
            4. Transition risks from climate policy affecting {sector}
            5. Climate-related opportunities for {sector} companies
            
            Search specifically for:
            - "{sector} TCFD climate risk disclosure"
            - "{sector} CDP climate change physical risk"
            - "{sector} climate transition risk carbon pricing"
            - "{company} climate risk sustainability report"
            
            Create a long-list of at least 8 climate risks and opportunities.
            Follow the exact format in your instructions.
            Include both physical AND transition risks.
            """
            
            # Run the agent
            result = agent.invoke({
                "messages": [("human", question)]
            })
            
            # Extract the output
            output = result["messages"][-1].content
        
        # ── Display results ───────────────────────────────
        st.success("✅ Analysis complete!")
        st.divider()
        
        # Show the company and sector as a subtitle
        st.subheader(f"Climate Risk Long-List: {company}")
        st.caption(f"Sector: {sector} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Display the output
        # st.markdown renders formatted text nicely
        st.markdown(output)
        
        st.divider()
        
        # ── Download button ───────────────────────────────
        # This creates a button that lets users download the results
        # as a text file — no saving to disk needed
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"risk_longlist_{company.replace(' ', '_')}_{timestamp}.txt"
        
        # Prepare the full content for download
        download_content = f"""CLIMATE RISK LONG-LIST
Company: {company}
Sector: {sector}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*60}

{output}"""
        
        # st.download_button creates a download button
        st.download_button(
            label="📥 Download Results as Text File",
            data=download_content,
            file_name=filename,
            mime="text/plain"
        )