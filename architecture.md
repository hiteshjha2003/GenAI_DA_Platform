Interpreted Architecture (Structured View)

1. User Interface Layer
   Streamlit App (UI)
   Custom CSS styling

This is where users:

Upload files
Enter natural language queries
View dashboards and outputs 2. Business Logic Layer
DataLoader
DataProcessor
DataVisualizer

Responsibilities:

Orchestrates the workflow
Controls data transformations
Sends processed data to visualization 3. Data Access Layer
DatabaseManager
SQL Server / PostgreSQL / MySQL connectivity
FileProcessor
Handles CSV, Excel, PDF, DOCX, TXT

Responsibilities:

Reading and writing data
Schema extraction
Data persistence 4. AI Layer (Core Intelligence)
LLMManager
OpenAI / Groq / Ollama
PromptEngine
Prompt templates & optimization
SQLGenerator
Converts Natural Language → SQL

Responsibilities:

Understanding user queries
Generating SQL or Python logic
Context-aware reasoning 5. External Systems
Databases (SQL systems)
LLM APIs (OpenAI, Groq)
Local Models (Ollama)
File Storage 6. Data Flow Pipeline
User → UI (Streamlit)
→ Input (Upload / Query)
→ AI Layer (NL Processing)
→ Data Layer (SQL / File Execution)
→ Processing Layer (Pandas / SQL)
→ Visualization Layer
→ Output (Dashboard / Export) 7. End-to-End Flow Explanation
User uploads file or connects database
User enters natural language query
Query goes to LLMManager
PromptEngine structures it
SQLGenerator creates query
DatabaseManager executes it
DataProcessor transforms results
DataVisualizer creates charts
Output shown in Streamlit + export option
