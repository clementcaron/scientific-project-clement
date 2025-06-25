"""
Streamlit interface for visualizing experiment results.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
import os


def load_results_data(results_dir="results"):
    """Load experiment results from JSON files."""
    results_path = Path(results_dir)
    
    if not results_path.exists():
        return None
    
    # Find the most recent results file
    json_files = list(results_path.glob("results_*.json"))
    if not json_files:
        return None
    
    latest_file = max(json_files, key=os.path.getctime)
    
    with open(latest_file, 'r') as f:
        data = json.load(f)
    
    return pd.DataFrame(data), latest_file


def create_success_rate_chart(df):
    """Create success rate comparison chart."""
    success_by_framework = df.groupby('framework')['success'].mean().reset_index()
    success_by_framework['success_rate'] = success_by_framework['success'] * 100
    
    fig = px.bar(
        success_by_framework, 
        x='framework', 
        y='success_rate',
        title='Success Rate by Framework',
        labels={'success_rate': 'Success Rate (%)', 'framework': 'Framework'},
        color='framework'
    )
    
    fig.update_layout(showlegend=False)
    return fig


def create_validation_score_chart(df):
    """Create validation score comparison chart."""
    fig = px.box(
        df, 
        x='framework', 
        y='validation_score',
        title='Validation Score Distribution by Framework',
        labels={'validation_score': 'Validation Score', 'framework': 'Framework'},
        color='framework'
    )
    
    return fig


def create_performance_metrics_chart(df):
    """Create performance metrics comparison."""
    metrics_by_framework = df.groupby('framework').agg({
        'execution_time': 'mean',
        'tokens_used': 'mean',
        'reasoning_steps': 'mean'
    }).reset_index()
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=['Avg Execution Time', 'Avg Tokens Used', 'Avg Reasoning Steps'],
        specs=[[{"secondary_y": False}, {"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Execution time
    fig.add_trace(
        go.Bar(x=metrics_by_framework['framework'], 
               y=metrics_by_framework['execution_time'],
               name='Execution Time',
               marker_color='lightblue'),
        row=1, col=1
    )
    
    # Tokens used
    fig.add_trace(
        go.Bar(x=metrics_by_framework['framework'], 
               y=metrics_by_framework['tokens_used'],
               name='Tokens Used',
               marker_color='lightgreen'),
        row=1, col=2
    )
    
    # Reasoning steps
    fig.add_trace(
        go.Bar(x=metrics_by_framework['framework'], 
               y=metrics_by_framework['reasoning_steps'],
               name='Reasoning Steps',
               marker_color='lightcoral'),
        row=1, col=3
    )
    
    fig.update_layout(
        title_text="Performance Metrics by Framework",
        showlegend=False,
        height=400
    )
    
    return fig


def create_task_type_performance_chart(df):
    """Create task type performance comparison."""
    task_performance = df.groupby(['task_type', 'framework']).agg({
        'validation_score': 'mean',
        'success': 'mean'
    }).reset_index()
    
    fig = px.bar(
        task_performance,
        x='task_type',
        y='validation_score',
        color='framework',
        barmode='group',
        title='Average Validation Score by Task Type and Framework',
        labels={'validation_score': 'Average Validation Score', 'task_type': 'Task Type'}
    )
    
    return fig


def create_consistency_chart(df):
    """Create consistency analysis chart."""
    # Calculate standard deviation of scores for each framework-task combination
    consistency = df.groupby(['framework', 'task_id']).agg({
        'validation_score': ['mean', 'std']
    }).reset_index()
    
    consistency.columns = ['framework', 'task_id', 'mean_score', 'score_std']
    consistency['score_std'] = consistency['score_std'].fillna(0)
    
    fig = px.scatter(
        consistency,
        x='mean_score',
        y='score_std',
        color='framework',
        title='Consistency Analysis: Mean Score vs Standard Deviation',
        labels={
            'mean_score': 'Mean Validation Score',
            'score_std': 'Standard Deviation',
            'framework': 'Framework'
        },
        hover_data=['task_id']
    )
    
    fig.add_annotation(
        x=0.02, y=0.98, xref="paper", yref="paper",
        text="Lower std = more consistent",
        showarrow=False, font=dict(size=10)
    )
    
    return fig


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="LLM Reasoning Framework Analysis",
        page_icon="🧠",
        layout="wide"
    )
    
    st.title("🧠 LLM Reasoning Framework Comparison")
    st.markdown("Analysis of ReAct, Chain-of-Thought, and Tree-of-Thoughts frameworks")
    
    # Load data
    data = load_results_data()
    
    if data is None:
        st.error("No experiment results found. Please run experiments first using `python run_experiment.py`")
        st.info("Expected results in the 'results/' directory as JSON files.")
        return
    
    df, results_file = data
    
    # Sidebar information
    st.sidebar.header("Experiment Info")
    st.sidebar.info(f"**Results file:** {results_file.name}")
    st.sidebar.info(f"**Total experiments:** {len(df)}")
    st.sidebar.info(f"**Frameworks:** {', '.join(df['framework'].unique())}")
    st.sidebar.info(f"**Task types:** {len(df['task_type'].unique())}")
    
    # Filter controls
    st.sidebar.header("Filters")
    
    selected_frameworks = st.sidebar.multiselect(
        "Select Frameworks",
        options=df['framework'].unique(),
        default=df['framework'].unique()
    )
    
    selected_task_types = st.sidebar.multiselect(
        "Select Task Types", 
        options=df['task_type'].unique(),
        default=df['task_type'].unique()
    )
    
    # Filter data
    filtered_df = df[
        (df['framework'].isin(selected_frameworks)) &
        (df['task_type'].isin(selected_task_types))
    ]
    
    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_success = filtered_df['success'].mean()
        st.metric("Overall Success Rate", f"{avg_success:.1%}")
    
    with col2:
        avg_score = filtered_df['validation_score'].mean()
        st.metric("Average Validation Score", f"{avg_score:.1f}")
    
    with col3:
        avg_time = filtered_df['execution_time'].mean()
        st.metric("Average Execution Time", f"{avg_time:.2f}s")
    
    with col4:
        avg_tokens = filtered_df['tokens_used'].mean()
        st.metric("Average Tokens Used", f"{avg_tokens:.0f}")
    
    # Charts
    st.header("Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(create_success_rate_chart(filtered_df), use_container_width=True)
    
    with col2:
        st.plotly_chart(create_validation_score_chart(filtered_df), use_container_width=True)
    
    st.plotly_chart(create_performance_metrics_chart(filtered_df), use_container_width=True)
    
    st.plotly_chart(create_task_type_performance_chart(filtered_df), use_container_width=True)
    
    st.plotly_chart(create_consistency_chart(filtered_df), use_container_width=True)
    
    # Detailed results table
    st.header("Detailed Results")
    
    # Summary table by framework
    summary_table = filtered_df.groupby('framework').agg({
        'success': ['count', 'sum', 'mean'],
        'validation_score': ['mean', 'std'],
        'execution_time': ['mean', 'std'],
        'tokens_used': ['mean', 'std'],
        'reasoning_steps': 'mean'
    }).round(2)
    
    summary_table.columns = [
        'Total Runs', 'Successful Runs', 'Success Rate',
        'Avg Score', 'Score Std', 'Avg Time', 'Time Std',
        'Avg Tokens', 'Token Std', 'Avg Steps'
    ]
    
    st.subheader("Summary by Framework")
    st.dataframe(summary_table)
    
    # Raw data table (optional)
    if st.checkbox("Show raw data"):
        st.subheader("Raw Results")
        display_columns = [
            'framework', 'task_id', 'task_type', 'run_number',
            'success', 'validation_score', 'execution_time', 
            'tokens_used', 'reasoning_steps'
        ]
        st.dataframe(filtered_df[display_columns])
    
    # Download buttons
    st.header("Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"experiment_results_filtered.csv",
            mime="text/csv"
        )
    
    with col2:
        summary_csv = summary_table.to_csv()
        st.download_button(
            label="Download Summary as CSV",
            data=summary_csv,
            file_name="experiment_summary.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
