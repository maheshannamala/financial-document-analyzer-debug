## Importing libraries and files
import os
from dotenv import load_dotenv
from crewai_tools import tool, SerperDevTool
from pypdf import PdfReader  # Requires: pip install pypdf

load_dotenv()

## Creating search tool
search_tool = SerperDevTool()

## Creating custom pdf reader tool
class FinancialDocumentTool:
    @tool("Read Financial Data")
    def read_data_tool(file_path: str):
        """
        Reads data from a PDF file at the specified path.
        Args:
            file_path (str): The path to the PDF file.
        Returns:
            str: The text content of the PDF.
        """
        try:
            reader = PdfReader(file_path)
            full_report = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_report += text + "\n"
            
            # Simple cleaning
            full_report = full_report.replace("\n\n", "\n")
            return full_report
        except Exception as e:
            return f"Error reading file: {str(e)}"

## Creating Investment Analysis Tool
class InvestmentTool:
    @tool("Analyze Investment")
    def analyze_investment_tool(financial_document_data: str):
        """Analyzes financial data for investment opportunities."""
        # Clean up the data format (simplified)
        processed_data = " ".join(financial_document_data.split())
        
        # logic placeholder
        return "Investment analysis based on the data provided."

## Creating Risk Assessment Tool
class RiskTool:
    @tool("Assess Risk")
    def create_risk_assessment_tool(financial_document_data: str):        
        """Assess risks based on financial data."""
        return "Risk assessment based on data provided."