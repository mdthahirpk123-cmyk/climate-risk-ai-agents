# Load your API keys from the .env file
from dotenv import load_dotenv
load_dotenv()

# Import the LLM connection
from langchain_openai import ChatOpenAI

# Import the updated Tavily search tool
from langchain_tavily import TavilySearch

# Import the correct agent builder for LangGraph 1.2.4
from langgraph.prebuilt import create_react_agent

# ── Step 1: Create the LLM ────────────────────────────────
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# ── Step 2: Create the search tool ───────────────────────
search_tool = TavilySearch(max_results=3)
tools = [search_tool]

# ── Step 3: Write your instructions ──────────────────────
# This is where your climate expertise goes
# The agent reads this before doing anything
system_prompt = """You are a senior climate risk analyst specialising 
in TCFD-aligned risk assessment. When identifying climate risks:
- Always separate PHYSICAL risks from TRANSITION risks
- Physical risks = floods, heat, water stress, storms
- Transition risks = policy changes, carbon pricing, technology shifts
- Always mention your source
- Be specific to the company sector"""

# ── Step 4: Create the agent ─────────────────────────────
# This combines LLM + tools + instructions into one agent
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_prompt
)

# ── Step 5: Ask it a question ────────────────────────────
result = agent.invoke({
    "messages": [
        ("human", """Search for physical climate risks for steel 
        manufacturers from TCFD reports or CDP disclosures. 
        List only physical risks with their sources.""")
    ]
})

# The answer is in the last message of the result
print("\n=== FINAL ANSWER ===")
print(result["messages"][-1].content)