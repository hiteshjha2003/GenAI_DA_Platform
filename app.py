import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from typing import Optional, Dict, Any

# Import our custom modules
from config.settings import settings
from core.db_manager import DatabaseManager
from core.data_loader import DataLoader
from core.processor import DataProcessor
from core.visualizer import DataVisualizer
from ai.llm_manager import LLMManager
from ai.sql_generator import SQLGenerator
from ai.prompt_engine import PromptEngine
from utils.logger import logger

# Page configuration
st.set_page_config(
    page_title="GenAI Data Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
def load_css():
    with open("assets/styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'data_loader' not in st.session_state:
    st.session_state.data_loader = DataLoader(st.session_state.db_manager)
if 'processor' not in st.session_state:
    st.session_state.processor = DataProcessor(st.session_state.data_loader)
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = DataVisualizer(st.session_state.data_loader)
if 'llm_manager' not in st.session_state:
    st.session_state.llm_manager = LLMManager()
if 'sql_generator' not in st.session_state:
    st.session_state.sql_generator = SQLGenerator(
        st.session_state.llm_manager,
        st.session_state.db_manager
    )
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def main():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 GenAI Data Analytics Platform</h1>
        <p>Transform your data with natural language queries and AI-powered insights</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<div class="sidebar">', unsafe_allow_html=True)
        st.header("⚙️ Configuration")

        # LLM Provider Selection
        available_providers = st.session_state.llm_manager.get_available_providers()
        if available_providers:
            current_provider = st.session_state.llm_manager.get_current_provider()
            selected_provider = st.selectbox(
                "LLM Provider",
                available_providers,
                index=available_providers.index(current_provider) if current_provider else 0
            )
            if selected_provider != current_provider:
                st.session_state.llm_manager.set_provider(selected_provider)
                st.success(f"Switched to {selected_provider}")

        # Database Connection
        st.subheader("SQL Server Connection")
        server = st.text_input("DB_SERVERNAME", value=settings.DB_SERVERNAME or "")
        database = st.text_input("DB_DATABASE", value=settings.DB_DATABASE or "")

        if st.button("Connect to SQL Server"):
            try:
                success = st.session_state.db_manager.connect_sqlserver(server, database)
                if success:
                    st.success("Connected to SQL Server successfully!")
                    update_schema_context()
                else:
                    st.error("Failed to connect to SQL Server")
            except Exception as e:
                st.error(f"Connection error: {e}")

        # Connection status and table explorer
        if st.session_state.db_manager.is_connected():
            st.success("✅ SQL Server Connected")
            if st.button("Fetch Tables"):
                try:
                    st.session_state.available_tables = st.session_state.db_manager.get_table_list()
                    st.success("Fetched table list successfully")
                except Exception as e:
                    st.error(f"Failed to fetch tables: {e}")

            available_tables = st.session_state.get('available_tables', [])
            if available_tables:
                selected_table = st.selectbox("Select a table to inspect", available_tables)
                st.markdown("---")
                st.subheader("Table Information")
                st.write(f"Selected table: **{selected_table}**")

                try:
                    schema_df = st.session_state.db_manager.get_table_schema(selected_table)
                    st.write(schema_df)
                except Exception as e:
                    st.error(f"Could not fetch schema for {selected_table}: {e}")
            else:
                st.info("Click 'Fetch Tables' to load available tables from the connected database.")
        else:
            st.warning("❌ Database Not Connected")

        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Data Upload Section
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📁 Data Upload")

        uploaded_file = st.file_uploader(
            "Upload your data file",
            type=settings.SUPPORTED_FILE_TYPES,
            help="Supported formats: CSV, Excel, TXT, PDF, DOCX"
        )

        if uploaded_file is not None:
            try:
                df = st.session_state.data_loader.load_from_upload(uploaded_file)
                st.success(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")

                # Data preview
                st.subheader("Data Preview")
                st.dataframe(df.head(), use_container_width=True)

                # Data quality metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Rows", len(df))
                with col_b:
                    st.metric("Columns", len(df.columns))
                with col_c:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                    st.metric("Null %", ".1f")

                # Upload to database option
                if st.session_state.db_manager.is_connected():
                    table_name = st.text_input("Table name for upload")
                    if st.button("Upload to Database") and table_name:
                        try:
                            st.session_state.data_loader.upload_to_database(table_name)
                            st.success(f"Uploaded to table: {table_name}")
                            update_schema_context()
                        except Exception as e:
                            st.error(f"Upload failed: {e}")

            except Exception as e:
                st.error(f"Error loading file: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

        # AI Chat Interface
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🤖 AI Assistant")

        # Chat history
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            for message in st.session_state.chat_history[-10:]:  # Show last 10 messages
                role_class = "user" if message["role"] == "user" else "assistant"
                st.markdown(f'<div class="chat-message {role_class}">{message["content"]}</div>',
                          unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Prompt input
        prompt = st.text_area(
            "Ask me anything about your data...",
            placeholder="e.g., 'Show me sales by region', 'Find customers with high spending', 'Create a chart of monthly trends'",
            height=100,
            key="prompt_input"
        )

        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("🚀 Execute", use_container_width=True) and prompt:
                execute_ai_query(prompt)

        with col2:
            if st.button("🧹 Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        with col3:
            if st.button("📊 Suggest Queries", use_container_width=True):
                suggest_queries()

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Results and Visualization Panel
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📊 Results & Visualizations")

        # Results display
        if 'last_result' in st.session_state:
            result = st.session_state.last_result

            if result.get('success'):
                if 'results' in result and isinstance(result['results'], pd.DataFrame):
                    df = result['results']
                    st.dataframe(df, use_container_width=True)

                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Export CSV"):
                            csv = df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="results.csv",
                                mime="text/csv"
                            )

                    with col2:
                        if st.button("📥 Export Excel"):
                            buffer = BytesIO()
                            df.to_excel(buffer, index=False)
                            st.download_button(
                                label="Download Excel",
                                data=buffer.getvalue(),
                                file_name="results.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

                if 'chart' in result:
                    st.plotly_chart(result['chart'], use_container_width=True)

            else:
                st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

        # Quick actions
        if st.session_state.data_loader.uploaded_data is not None:
            st.subheader("Quick Actions")

            if st.button("🧹 Clean Data"):
                try:
                    cleaned_df = st.session_state.data_loader.clean_data()
                    st.success("Data cleaned successfully!")
                    st.session_state.last_result = {
                        'success': True,
                        'results': cleaned_df.head(),
                        'message': 'Data cleaned'
                    }
                except Exception as e:
                    st.error(f"Cleaning failed: {e}")

            if st.button("📈 Generate Insights"):
                generate_insights()

        st.markdown('</div>', unsafe_allow_html=True)

def execute_ai_query(prompt: str):
    """Execute AI-powered query."""
    try:
        # Add user message to chat
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Determine query type and execute
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['select', 'show', 'find', 'get', 'count', 'sum', 'average', 'query']):
            # SQL Query
            result = st.session_state.sql_generator.execute_generated_sql(prompt)
            if result['success']:
                response = f"Here's the result of your query:\n\n**SQL Query:**\n```sql\n{result['query']}\n```"
            else:
                response = f"I encountered an error: {result.get('error', 'Unknown error')}"

        elif any(word in prompt_lower for word in ['transform', 'filter', 'group', 'aggregate', 'clean', 'process']):
            # Python transformation
            if st.session_state.data_loader.uploaded_data is None:
                response = "Please upload data first before applying transformations."
            else:
                df_info = {
                    'columns': list(st.session_state.data_loader.uploaded_data.columns),
                    'dtypes': st.session_state.data_loader.uploaded_data.dtypes.to_dict()
                }
                prompt_engine = PromptEngine(df_info)
                transform_prompt = prompt_engine.generate_python_transform_prompt(prompt, df_info)
                code = st.session_state.llm_manager.generate_response(transform_prompt)

                try:
                    result_df = st.session_state.processor.execute_python_transformation(code)
                    response = f"Transformation applied successfully!\n\n**Generated Code:**\n```python\n{code}\n```"
                    result = {'success': True, 'results': result_df.head()}
                except Exception as e:
                    response = f"Transformation failed: {e}"
                    result = {'success': False, 'error': str(e)}

        elif any(word in prompt_lower for word in ['chart', 'plot', 'visualize', 'graph']):
            # Visualization
            if st.session_state.data_loader.uploaded_data is None:
                response = "Please upload data first before creating visualizations."
            else:
                suggestions = st.session_state.visualizer.get_visualization_suggestions()
                if suggestions:
                    config = suggestions[0]  # Use first suggestion
                    chart = st.session_state.visualizer.create_plotly_chart(
                        config['type'], config['x'], config['y'], title=config.get('title', '')
                    )
                    response = f"Created {config['type']} chart for {config['x']} vs {config['y']}"
                    result = {'success': True, 'chart': chart}
                else:
                    response = "Couldn't determine appropriate visualization for your data."
                    result = {'success': False, 'error': 'No visualization suggestions available'}

        else:
            # General query - try to understand intent
            response = st.session_state.llm_manager.generate_response(
                f"Analyze this data-related query and provide a helpful response: {prompt}"
            )
            result = {'success': True, 'message': response}

        # Add assistant response to chat
        st.session_state.chat_history.append({"role": "assistant", "content": response})

        # Store result for display
        if 'result' not in locals():
            result = {'success': True, 'message': response}
        st.session_state.last_result = result

        st.rerun()

    except Exception as e:
        error_msg = f"An error occurred: {e}"
        st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
        st.session_state.last_result = {'success': False, 'error': error_msg}
        st.rerun()

def suggest_queries():
    """Generate query suggestions."""
    if st.session_state.data_loader.uploaded_data is not None:
        columns = list(st.session_state.data_loader.uploaded_data.columns)
        suggestions = [
            f"Show me the distribution of {columns[0] if columns else 'data'}",
            f"Find records where {columns[0] if columns else 'column'} is not null",
            f"Calculate summary statistics for {', '.join(columns[:3])}",
            f"Show me the top 10 records by {columns[0] if columns else 'first column'}"
        ]
    elif st.session_state.db_manager.is_connected():
        tables = st.session_state.db_manager.get_table_list()
        if tables:
            suggestions = [
                f"Show me all records from {tables[0]}",
                f"Count total records in {tables[0]}",
                f"Show me the structure of {tables[0]}",
                "List all available tables"
            ]
        else:
            suggestions = ["Connect to a database first"]
    else:
        suggestions = ["Upload data or connect to a database to get suggestions"]

    suggestion_text = "💡 **Suggested Queries:**\n\n" + "\n".join(f"• {s}" for s in suggestions)
    st.session_state.chat_history.append({"role": "assistant", "content": suggestion_text})
    st.rerun()

def generate_insights():
    """Generate automatic data insights."""
    if st.session_state.data_loader.uploaded_data is None:
        st.error("No data available for insights")
        return

    try:
        df = st.session_state.data_loader.uploaded_data
        df_info = {
            'shape': df.shape,
            'columns': list(df.columns),
            'dtypes': df.dtypes.to_dict()
        }

        prompt_engine = PromptEngine(df_info)
        insight_prompt = prompt_engine.generate_data_insights_prompt(df_info)
        sample_data = df.head().to_string()

        full_prompt = f"{insight_prompt}\n\nDataset Sample:\n{sample_data}"

        insights = st.session_state.llm_manager.generate_response(full_prompt)

        insight_text = f"🔍 **Data Insights:**\n\n{insights}"
        st.session_state.chat_history.append({"role": "assistant", "content": insight_text})
        st.rerun()

    except Exception as e:
        st.error(f"Failed to generate insights: {e}")

def update_schema_context():
    """Update schema information for AI context."""
    if st.session_state.db_manager.is_connected():
        try:
            tables = st.session_state.db_manager.get_table_list()
            schema_info = {'tables': tables, 'columns': {}}

            for table in tables[:5]:  # Limit to first 5 tables for context
                try:
                    columns_df = st.session_state.db_manager.get_table_schema(table)
                    if not columns_df.empty:
                        columns = columns_df.iloc[:, 0].tolist()  # First column is column name
                        schema_info['columns'][table] = columns
                except Exception as e:
                    logger.warning(f"Could not get schema for table {table}: {e}")

            st.session_state.sql_generator.update_schema_context(schema_info)
        except Exception as e:
            logger.error(f"Error updating schema context: {e}")

if __name__ == "__main__":
    main()