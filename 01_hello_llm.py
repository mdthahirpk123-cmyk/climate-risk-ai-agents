# This goes to your .env file and loads your API keys into memory
# Without this line, your code won't know your OpenAI key exists
from dotenv import load_dotenv
load_dotenv()

# This imports the tool that connects your code to GPT
# Think of it as picking up the phone to call OpenAI
from langchain_openai import ChatOpenAI

# This creates your connection to GPT
# gpt-4o-mini is cheaper — perfect for testing
# temperature=0 means answers will be consistent, not random
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# This sends your question to GPT and waits for the answer
# .invoke() means "send this and give me a response back"
response = llm.invoke("What are the top 3 physical climate risks for a steel manufacturer?")

# This prints GPT's answer in your terminal below
print(response.content)