# Financial Document Analyzer API

A backend service built with FastAPI and CrewAI that utilizes AI agents to analyze financial documents (PDFs) and generate investment insights. 

**Note:** The agents in this project are configured with satirical and "creative" backstories (e.g., instructing the AI to "make up investment advice"). This is a stylistic choice for the specific application behavior and not a standard financial compliance tool.

---

## 🐛 Bugs Identified and Resolved

The initial codebase contained several critical bugs spanning agent configuration, tool definitions, and API integration. Below is a breakdown of the issues found and how they were fixed:

### 1. `tools.py` (Custom Tool Definitions)
* **Missing Dependencies:** The original code attempted to use a `Pdf` class that was never imported or defined. **Fix:** Integrated `pypdf` (`PdfReader`) to handle document parsing securely and reliably.
* **Missing Decorators:** CrewAI requires custom tools to be decorated so the agents recognize them as executable functions. **Fix:** Applied the `@tool` decorator to all custom agent actions (`read_data_tool`, `analyze_investment_tool`, `create_risk_assessment_tool`).
* **Logic Errors & Inefficiencies:** The `InvestmentTool` contained a `while` loop that manually modified strings by index (`processed_data[:i] + ...`), which is highly inefficient and prone to infinite loops. **Fix:** Replaced the loop with standard, safe Python string methods (`" ".join(string.split())`).

### 2. `agents.py` (Agent Initialization)
* **Self-Assignment Error:** The LLM was assigned to itself (`llm = llm`) before being instantiated, throwing a `NameError`. **Fix:** Properly initialized an LLM instance using `from crewai import LLM` and instantiated it (e.g., `LLM(model="gpt-4o")`).
* **Argument Mismatch:** The `Agent` constructor requires a list passed to the `tools` parameter, but the code used the singular `tool`. **Fix:** Renamed the parameter to `tools`.
* **Tool Invocation:** The raw class methods were being passed into the tools list without being proper tool objects. **Fix:** Passed the newly decorated tool methods.

### 3. `task.py` (Task Execution Logic)
* **Agent Misallocation:** The `verification` task was incorrectly assigned to the `financial_analyst` agent despite the descriptions requiring the `verifier`. **Fix:** Reassigned `agent=verifier`.
* **Missing Context:** Tasks required the file path to execute the PDF reader tool, but no placeholders were provided. **Fix:** Added `{file_path}` placeholders directly into the task descriptions so the agents know exactly which file to process.

### 4. `main.py` (FastAPI Server & Crew Execution)
* **Input Data Passing:** The `financial_crew.kickoff()` method only received the `query`, leaving the agents blind to the uploaded file's location. **Fix:** Updated the `inputs` dictionary in `kickoff` to include both `query` and `file_path`.
* **File Handling & Race Conditions:** The application saved files relative to the execution path, which can cause OS-level "file not found" errors during cleanup if paths are not absolute. **Fix:** Implemented safer `os.path.abspath` handling and wrapped file cleanup in a safer `try/except` block to prevent the API from crashing during teardown.

---

## ⚙️ Setup and Installation

### Prerequisites
* Python 3.10+
* An OpenAI API Key (or other supported LLM provider)
* A Serper API Key (for the search tool)

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/financial-document-analyzer.git](https://github.com/yourusername/financial-document-analyzer.git)
    cd financial-document-analyzer
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install crewai crewai-tools fastapi uvicorn python-dotenv pypdf pydantic
    ```

4.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add your API keys:
    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    SERPER_API_KEY=your_serper_api_key_here
    ```

---

## 🚀 Usage Instructions

1.  **Start the FastAPI server:**
    ```bash
    python main.py
    ```
    *(Alternatively, run via Uvicorn directly: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`)*

2.  **Access the Swagger UI:**
    Open your browser and navigate to `http://localhost:8000/docs` to interact with the API directly from the auto-generated Swagger dashboard.

---

## 📚 API Documentation

### 1. Health Check
* **Endpoint:** `/`
* **Method:** `GET`
* **Description:** Verifies that the server is up and running.
* **Response:**
    ```json
    {
      "message": "Financial Document Analyzer API is running"
    }
    ```

### 2. Analyze Financial Document
* **Endpoint:** `/analyze`
* **Method:** `POST`
* **Content-Type:** `multipart/form-data`
* **Description:** Uploads a PDF document and an optional text query. The CrewAI agents process the document and return a detailed, multi-agent analysis.

#### Request Parameters:
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `file` | File (PDF) | **Yes** | The financial document to be analyzed. |
| `query` | Form (String)| No | Custom instructions or questions for the AI. Defaults to *"Analyze this financial document for investment insights"*. |

#### Success Response (200 OK):
```json
{
  "status": "success",
  "query": "Analyze this financial document for investment insights",
  "analysis": "[Detailed string output containing the AI agents' combined analysis, market predictions, and risk assessments...]",
  "file_processed": "sample_report.pdf"
}
