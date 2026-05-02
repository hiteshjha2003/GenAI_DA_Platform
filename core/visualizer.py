import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import matplotlib.pyplot as plt
import streamlit as st
from typing import Dict, Any, Optional, List
from utils.logger import logger

class DataVisualizer:
    """Handles data visualization and dashboard creation."""

    def __init__(self, data_loader):
        self.data_loader = data_loader

    def create_plotly_chart(self, chart_type: str, x_col: str, y_col: str,
                          color_col: Optional[str] = None, size_col: Optional[str] = None,
                          title: str = "") -> go.Figure:
        """Create Plotly chart."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded for visualization")

        try:
            df = self.data_loader.uploaded_data

            if chart_type == 'bar':
                fig = px.bar(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'line':
                fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'scatter':
                fig = px.scatter(df, x=x_col, y=y_col, color=color_col, size=size_col, title=title)
            elif chart_type == 'pie':
                fig = px.pie(df, names=x_col, values=y_col, title=title)
            elif chart_type == 'histogram':
                fig = px.histogram(df, x=x_col, color=color_col, title=title)
            elif chart_type == 'box':
                fig = px.box(df, x=x_col, y=y_col, color=color_col, title=title)
            elif chart_type == 'heatmap':
                # For heatmap, we need to pivot the data
                pivot_df = df.pivot(index=x_col, columns=y_col, values=size_col) if size_col else df.pivot(index=x_col, columns=y_col)
                fig = px.imshow(pivot_df, title=title)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            return fig
        except Exception as e:
            logger.error(f"Error creating Plotly chart: {e}")
            raise

    def create_altair_chart(self, chart_type: str, x_col: str, y_col: str,
                          color_col: Optional[str] = None, title: str = "") -> alt.Chart:
        """Create Altair chart."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded for visualization")

        try:
            df = self.data_loader.uploaded_data

            if chart_type == 'bar':
                chart = alt.Chart(df).mark_bar().encode(
                    x=x_col,
                    y=y_col,
                    color=color_col
                ).properties(title=title)
            elif chart_type == 'line':
                chart = alt.Chart(df).mark_line().encode(
                    x=x_col,
                    y=y_col,
                    color=color_col
                ).properties(title=title)
            elif chart_type == 'scatter':
                chart = alt.Chart(df).mark_circle().encode(
                    x=x_col,
                    y=y_col,
                    color=color_col
                ).properties(title=title)
            elif chart_type == 'area':
                chart = alt.Chart(df).mark_area().encode(
                    x=x_col,
                    y=y_col,
                    color=color_col
                ).properties(title=title)
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            return chart
        except Exception as e:
            logger.error(f"Error creating Altair chart: {e}")
            raise

    def create_matplotlib_chart(self, chart_type: str, x_col: str, y_col: str,
                              title: str = "") -> plt.Figure:
        """Create Matplotlib chart."""
        if self.data_loader.uploaded_data is None:
            raise ValueError("No data loaded for visualization")

        try:
            df = self.data_loader.uploaded_data
            fig, ax = plt.subplots(figsize=(10, 6))

            if chart_type == 'bar':
                ax.bar(df[x_col], df[y_col])
            elif chart_type == 'line':
                ax.plot(df[x_col], df[y_col])
            elif chart_type == 'scatter':
                ax.scatter(df[x_col], df[y_col])
            elif chart_type == 'histogram':
                ax.hist(df[x_col])
            else:
                raise ValueError(f"Unsupported chart type: {chart_type}")

            ax.set_title(title)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            plt.xticks(rotation=45)

            return fig
        except Exception as e:
            logger.error(f"Error creating Matplotlib chart: {e}")
            raise

    def create_dashboard(self, charts_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a dashboard with multiple charts."""
        dashboard = {}

        try:
            for i, config in enumerate(charts_config):
                chart_type = config.get('type', 'bar')
                x_col = config.get('x')
                y_col = config.get('y')
                title = config.get('title', f'Chart {i+1}')
                library = config.get('library', 'plotly')

                if library == 'plotly':
                    chart = self.create_plotly_chart(chart_type, x_col, y_col, title=title)
                elif library == 'altair':
                    chart = self.create_altair_chart(chart_type, x_col, y_col, title=title)
                elif library == 'matplotlib':
                    chart = self.create_matplotlib_chart(chart_type, x_col, y_col, title=title)
                else:
                    raise ValueError(f"Unsupported visualization library: {library}")

                dashboard[f'chart_{i+1}'] = {
                    'chart': chart,
                    'config': config
                }

            logger.info(f"Dashboard created with {len(charts_config)} charts")
            return dashboard
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            raise

    def get_visualization_suggestions(self) -> List[Dict[str, Any]]:
        """Suggest appropriate visualizations based on data."""
        if self.data_loader.uploaded_data is None:
            return []

        try:
            df = self.data_loader.uploaded_data
            suggestions = []

            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

            # Suggest bar chart for categorical vs numeric
            if categorical_cols and numeric_cols:
                suggestions.append({
                    'type': 'bar',
                    'x': categorical_cols[0],
                    'y': numeric_cols[0],
                    'title': f'{numeric_cols[0]} by {categorical_cols[0]}'
                })

            # Suggest scatter plot for numeric vs numeric
            if len(numeric_cols) >= 2:
                suggestions.append({
                    'type': 'scatter',
                    'x': numeric_cols[0],
                    'y': numeric_cols[1],
                    'title': f'{numeric_cols[1]} vs {numeric_cols[0]}'
                })

            # Suggest histogram for numeric columns
            if numeric_cols:
                suggestions.append({
                    'type': 'histogram',
                    'x': numeric_cols[0],
                    'title': f'Distribution of {numeric_cols[0]}'
                })

            # Suggest pie chart for categorical with few unique values
            if categorical_cols:
                cat_col = categorical_cols[0]
                if df[cat_col].nunique() <= 10:
                    suggestions.append({
                        'type': 'pie',
                        'x': cat_col,
                        'y': cat_col,  # For pie chart, names and values are the same
                        'title': f'Distribution of {cat_col}'
                    })

            return suggestions
        except Exception as e:
            logger.error(f"Error generating visualization suggestions: {e}")
            return []