"""
FastAPI application for the GenAI Data Analytics Platform.
Backend server that handles file uploads, AI queries, database operations, and charting.
"""

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import pandas as pd
from docx import Document
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PyPDF2 import PdfReader


SUPPORTED_FILE_TYPES = {
    ".csv": "table",
    ".xlsx": "table",
    ".xls": "table",
    ".txt": "document",
    ".pdf": "document",
    ".docx": "document",
}
PREVIEW_ROW_LIMIT = 10
QUERY_ROW_LIMIT = 200
TEXT_PREVIEW_LIMIT = 4000


app = FastAPI(
    title="GenAI Data Analytics Platform API",
    description="API for GenAI Data Analytics Platform",
    version="1.0.0",
)

# Configure CORS to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# In-memory data store for demo mode
data_store = {
    "datasets": [],
    "queries": [],
    "charts": [],
    "active_dataset_id": None,
}


def normalize_value(value: Any) -> Any:
    """Convert pandas and Python values into JSON-safe values."""
    if value is None:
        return ""

    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    if pd.isna(value):
        return ""

    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass

    return value


def dataframe_to_records(df: pd.DataFrame, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Serialize a DataFrame into JSON-safe row records."""
    working_df = df.copy()
    if limit is not None:
        working_df = working_df.head(limit)

    working_df = working_df.where(pd.notna(working_df), "")

    records: List[Dict[str, Any]] = []
    for row in working_df.to_dict(orient="records"):
        serialized_row = {str(key): normalize_value(value) for key, value in row.items()}
        records.append(serialized_row)

    return records


def extract_pdf_text(content: bytes) -> str:
    """Extract text from PDF file."""
    reader = PdfReader(BytesIO(content))
    extracted = []
    for page in reader.pages:
        extracted.append((page.extract_text() or "").strip())
    return "\n".join(part for part in extracted if part).strip()


def extract_docx_text(content: bytes) -> str:
    """Extract text from DOCX file."""
    document = Document(BytesIO(content))
    lines = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(lines).strip()


def build_document_preview(text: str) -> List[Dict[str, str]]:
    """Build preview for document files."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        compact_text = " ".join(text.split())
        if compact_text:
            lines = [compact_text[index:index + 280] for index in range(0, len(compact_text), 280)]
        else:
            lines = ["No readable text was extracted from this file."]

    return [{"content": line[:280]} for line in lines[:PREVIEW_ROW_LIMIT]]


def parse_uploaded_file(filename: str, content: bytes) -> Dict[str, Any]:
    """Parse uploaded file and extract data."""
    extension = Path(filename).suffix.lower()
    dataset_kind = SUPPORTED_FILE_TYPES.get(extension)

    if not dataset_kind:
        allowed = ", ".join(sorted(SUPPORTED_FILE_TYPES))
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{extension}'. Allowed: {allowed}")

    if dataset_kind == "table":
        if extension == ".csv":
            dataframe = pd.read_csv(BytesIO(content))
        else:
            dataframe = pd.read_excel(BytesIO(content))

        columns = [str(column) for column in dataframe.columns.tolist()]
        preview = dataframe_to_records(dataframe, PREVIEW_ROW_LIMIT)
        records = dataframe_to_records(dataframe, QUERY_ROW_LIMIT)

        return {
            "dataset_kind": "table",
            "columns": columns,
            "row_count": int(len(dataframe)),
            "column_count": int(len(columns)),
            "preview": preview,
            "records": records,
            "query_context": (
                f"Tabular dataset with {len(dataframe)} rows and columns: {', '.join(columns)}."
            ),
        }

    # Handle document files
    if extension == ".txt":
        text_content = content.decode("utf-8", errors="ignore").strip()
    elif extension == ".pdf":
        text_content = extract_pdf_text(content)
    else:
        text_content = extract_docx_text(content)

    text_content = text_content.strip()
    preview = build_document_preview(text_content)
    preview_text = text_content[:TEXT_PREVIEW_LIMIT] if text_content else ""

    return {
        "dataset_kind": "document",
        "columns": ["content"],
        "row_count": max(len(preview), 1),
        "column_count": 1,
        "preview": preview,
        "records": preview,
        "text_content": text_content,
        "text_excerpt": preview_text,
        "query_context": preview_text or "Document uploaded but no readable text was extracted.",
    }


def public_dataset_payload(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Return dataset payload without sensitive internal fields."""
    hidden_keys = {"records", "query_context", "text_content"}
    return {key: value for key, value in dataset.items() if key not in hidden_keys}


def get_active_dataset() -> Optional[Dict[str, Any]]:
    """Get currently active dataset."""
    active_id = data_store.get("active_dataset_id")
    if active_id is None:
        return None

    for dataset in data_store["datasets"]:
        if dataset["id"] == active_id:
            return dataset

    return None


def find_matching_column(prompt: str, columns: List[str]) -> Optional[str]:
    """Find column name matching the prompt."""
    prompt_lower = prompt.lower()
    for column in columns:
        if column.lower() in prompt_lower:
            return column
    return None


def build_table_query_response(prompt: str, dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Build response for table queries."""
    records = dataset.get("records", [])
    filename = dataset["filename"]

    if not records:
        return {
            "answer": f"{filename} was uploaded, but there is no tabular preview available to analyze yet.",
            "result": {"columns": [], "data": []},
            "sql_generated": None,
        }

    dataframe = pd.DataFrame(records)
    prompt_lower = prompt.lower()
    row_count = dataset.get("row_count", len(dataframe))
    column_count = dataset.get("column_count", len(dataframe.columns))

    numeric_frame = dataframe.apply(pd.to_numeric, errors="coerce")
    numeric_columns = [column for column in dataframe.columns if numeric_frame[column].notna().any()]

    if "how many" in prompt_lower or "count" in prompt_lower or "rows" in prompt_lower:
        result = {
            "columns": ["metric", "value"],
            "data": [
                {"metric": "rows", "value": row_count},
                {"metric": "columns", "value": column_count},
            ],
        }
        return {
            "answer": (
                f"{filename} contains {row_count} rows and {column_count} columns. "
                "I have also returned the dataset size summary."
            ),
            "result": result,
            "sql_generated": None,
        }

    stats_keywords = ("sum", "total", "average", "avg", "mean", "max", "min")
    if numeric_columns and any(keyword in prompt_lower for keyword in stats_keywords):
        target_column = find_matching_column(prompt, numeric_columns) or numeric_columns[0]
        series = pd.to_numeric(dataframe[target_column], errors="coerce").dropna()

        result = {
            "columns": ["metric", "value"],
            "data": [
                {"metric": "sum", "value": round(float(series.sum()), 2)},
                {"metric": "average", "value": round(float(series.mean()), 2)},
                {"metric": "min", "value": round(float(series.min()), 2)},
                {"metric": "max", "value": round(float(series.max()), 2)},
            ],
        }
        return {
            "answer": (
                f"I analyzed the numeric column '{target_column}' from {filename} and returned "
                "its sum, average, minimum, and maximum values."
            ),
            "result": result,
            "sql_generated": None,
        }

    selected_columns = list(dataframe.columns[: min(5, len(dataframe.columns))])
    matched_column = find_matching_column(prompt, list(dataframe.columns))
    if matched_column:
        selected_columns = [matched_column]

    preview_frame = dataframe[selected_columns].head(PREVIEW_ROW_LIMIT)
    return {
        "answer": (
            f"I used the uploaded dataset '{filename}' and returned a preview of the most relevant rows "
            "for your question."
        ),
        "result": {
            "columns": [str(column) for column in preview_frame.columns.tolist()],
            "data": dataframe_to_records(preview_frame),
        },
        "sql_generated": None,
    }


def build_document_query_response(prompt: str, dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Build response for document queries."""
    filename = dataset["filename"]
    text_content = dataset.get("text_content", "") or dataset.get("query_context", "")

    if not text_content:
        return {
            "answer": f"{filename} was uploaded, but no readable text could be extracted from it.",
            "result": {"columns": ["content"], "data": dataset.get("preview", [])},
            "sql_generated": None,
        }

    prompt_terms = {term for term in prompt.lower().split() if len(term) > 3}
    lines = [line.strip() for line in text_content.splitlines() if line.strip()]

    matched_lines = []
    for line in lines:
        lower_line = line.lower()
        if any(term in lower_line for term in prompt_terms):
            matched_lines.append(line)
        if len(matched_lines) >= PREVIEW_ROW_LIMIT:
            break

    if not matched_lines:
        matched_lines = [row["content"] for row in dataset.get("preview", [])[:PREVIEW_ROW_LIMIT]]

    result_rows = [{"content": line[:280]} for line in matched_lines[:PREVIEW_ROW_LIMIT]]

    return {
        "answer": (
            f"I searched the uploaded document '{filename}' and returned the most relevant extracted text "
            "snippets I could find for your question."
        ),
        "result": {"columns": ["content"], "data": result_rows},
        "sql_generated": None,
    }


def build_query_response(prompt: str, provider: str, data_context: Optional[str]) -> Dict[str, Any]:
    """Build response for AI queries."""
    active_dataset = get_active_dataset()

    if active_dataset:
        if active_dataset["dataset_kind"] == "document":
            response = build_document_query_response(prompt, active_dataset)
        else:
            response = build_table_query_response(prompt, active_dataset)
        response["context_source"] = active_dataset["filename"]
        response["provider"] = provider
        return response

    fallback_answer = "No uploaded dataset is currently active."
    if data_context:
        fallback_answer = f"I received your question and context hint: {data_context}"

    return {
        "answer": fallback_answer,
        "result": {"columns": [], "data": []},
        "sql_generated": None,
        "context_source": None,
        "provider": provider,
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API is running."""
    return {
        "status": "ok",
        "message": "GenAI Data Analytics Platform API",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "llm_providers": ["openai", "groq", "ollama"],
        "datasets_loaded": len(data_store["datasets"]),
    }


@app.get("/api/health")
async def api_health():
    """API health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "llm_providers": ["openai", "groq", "ollama"],
        "datasets_loaded": len(data_store["datasets"]),
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload and parse file (CSV, Excel, PDF, DOCX, TXT)."""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="A filename is required.")

        content = await file.read()
        parsed_dataset = parse_uploaded_file(file.filename, content)

        file_info = {
            "id": len(data_store["datasets"]) + 1,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "status": "uploaded",
            **parsed_dataset,
        }

        data_store["datasets"].append(file_info)
        data_store["active_dataset_id"] = file_info["id"]

        return {
            "success": True,
            "message": "File uploaded successfully",
            "file": public_dataset_payload(file_info),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/datasets")
async def get_datasets():
    """Get all uploaded datasets."""
    return {
        "success": True,
        "datasets": [public_dataset_payload(dataset) for dataset in data_store["datasets"]],
        "active_dataset_id": data_store.get("active_dataset_id"),
    }


@app.delete("/api/datasets/{dataset_id}")
async def delete_dataset(dataset_id: int):
    """Delete a dataset by ID."""
    try:
        data_store["datasets"] = [dataset for dataset in data_store["datasets"] if dataset["id"] != dataset_id]
        if data_store.get("active_dataset_id") == dataset_id:
            data_store["active_dataset_id"] = data_store["datasets"][-1]["id"] if data_store["datasets"] else None
        return {"success": True, "message": "Dataset deleted"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/database/connect")
async def connect_database(
    server: str = Form(...),
    database: str = Form(...),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
):
    """Connect to SQL Server database."""
    return {
        "success": True,
        "message": f"Connected to {database} on {server}",
        "tables": [
            "Customers",
            "Orders",
            "Products",
            "Sales",
            "Employees",
        ],
    }


@app.get("/api/database/tables")
async def get_tables():
    """Get list of database tables."""
    return {
        "success": True,
        "tables": [
            {"name": "Customers", "rows": 1250},
            {"name": "Orders", "rows": 5430},
            {"name": "Products", "rows": 350},
            {"name": "Sales", "rows": 15000},
            {"name": "Employees", "rows": 85},
        ],
    }


@app.get("/api/database/tables/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get schema for a specific table."""
    schemas = {
        "Customers": [
            {"column": "CustomerID", "type": "INT", "nullable": "NO", "key": "PK"},
            {"column": "Name", "type": "VARCHAR(100)", "nullable": "NO", "key": ""},
            {"column": "Email", "type": "VARCHAR(255)", "nullable": "YES", "key": ""},
            {"column": "Phone", "type": "VARCHAR(20)", "nullable": "YES", "key": ""},
            {"column": "CreatedAt", "type": "DATETIME", "nullable": "NO", "key": ""},
        ],
        "Orders": [
            {"column": "OrderID", "type": "INT", "nullable": "NO", "key": "PK"},
            {"column": "CustomerID", "type": "INT", "nullable": "NO", "key": "FK"},
            {"column": "OrderDate", "type": "DATETIME", "nullable": "NO", "key": ""},
            {"column": "TotalAmount", "type": "DECIMAL(10,2)", "nullable": "NO", "key": ""},
            {"column": "Status", "type": "VARCHAR(20)", "nullable": "NO", "key": ""},
        ],
    }

    return {
        "success": True,
        "table": table_name,
        "schema": schemas.get(table_name, []),
    }


@app.post("/api/query")
async def execute_query(
    prompt: str = Form(...),
    provider: str = Form("openai"),
    data_context: Optional[str] = Form(None),
):
    """Execute AI query on uploaded data."""
    query_payload = build_query_response(prompt, provider, data_context)
    query_result = {
        "id": len(data_store["queries"]) + 1,
        "prompt": prompt,
        "provider": provider,
        "answer": query_payload["answer"],
        "result": query_payload["result"],
        "sql_generated": query_payload.get("sql_generated"),
        "context_source": query_payload.get("context_source"),
    }

    data_store["queries"].append(query_result)

    return {
        "success": True,
        "query": query_result,
    }


@app.get("/api/queries")
async def get_query_history():
    """Get query history."""
    return {
        "success": True,
        "queries": data_store["queries"],
    }


@app.post("/api/charts")
async def create_chart(
    chart_type: str = Form(...),
    x_axis: str = Form(...),
    y_axis: str = Form(...),
    title: str = Form("Data Visualization"),
    data: str = Form(...),
):
    """Create a chart from data."""
    try:
        chart_data = json.loads(data)

        chart = {
            "id": len(data_store["charts"]) + 1,
            "type": chart_type,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "title": title,
            "data": chart_data,
        }

        data_store["charts"].append(chart)

        return {
            "success": True,
            "chart": chart,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/charts")
async def get_charts():
    """Get all charts."""
    return {
        "success": True,
        "charts": data_store["charts"],
    }


@app.get("/api/settings")
async def get_settings():
    """Get application settings."""
    return {
        "success": True,
        "settings": {
            "default_provider": "openai",
            "theme": "light",
            "ollama_url": "http://localhost:11434",
        },
    }


@app.post("/api/settings")
async def update_settings(settings: Dict[str, Any]):
    """Update application settings."""
    return {
        "success": True,
        "message": "Settings updated successfully",
    }


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
