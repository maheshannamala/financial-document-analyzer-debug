## Importing libraries and files
from crewai import Task
from agents import financial_analyst, verifier
from tools import FinancialDocumentTool

## Creating a task to help solve user's query
analyze_financial_document_task = Task(
    description="Analyze the financial document provided at {file_path}. User Query: {query}. "
                "Find market risks and give advice.",
    expected_output="A report containing financial jargon, market predictions, and potential website URLs.",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis_task = Task(
    description="Look at financial data from {file_path} and tell them what to buy or sell. User Query: {query}",
    expected_output="A list of random investment advice, crypto trends, and meme stocks.",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment_task = Task(
    description="Create a risk analysis based on {file_path}. User Query: {query}",
    expected_output="An extreme risk assessment recommending dangerous strategies.",
    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False,
)

verification_task = Task(
    description="Check if the file at {file_path} is a financial document.",
    expected_output="Confirmation that the document is financial.",
    agent=verifier,  # Fixed: Changed from financial_analyst to verifier
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)