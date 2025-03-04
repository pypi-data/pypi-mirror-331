"""Module for generating HTML reports from cleaning statistics."""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import plotly.graph_objects as go
from jinja2 import Environment, PackageLoader, select_autoescape

def create_pie_chart(labels: List[str], values: List[int], title: str) -> str:
    """Create a pie chart using plotly.

    Args:
        labels: Labels for pie chart segments
        values: Values for pie chart segments
        title: Title of the chart

    Returns:
        HTML string of the chart
    """
    # Filter out zero values for display purposes
    non_zero_indices = [i for i, val in enumerate(values) if val > 0]
    filtered_labels = [labels[i] for i in non_zero_indices]
    filtered_values = [values[i] for i in non_zero_indices]
    
    fig = go.Figure(data=[go.Pie(
        labels=filtered_labels, 
        values=filtered_values, 
        hole=.3,
        textinfo='label+percent'
    )])
    fig.update_layout(title=title)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def create_box_plot(data: Dict[str, Dict], title: str) -> str:
    """Create a box plot for length statistics.

    Args:
        data: Dictionary containing length statistics
        title: Title of the plot

    Returns:
        HTML string of the plot
    """
    fig = go.Figure()
    
    for lang, stats in data.items():
        fig.add_trace(go.Box(
            y=[stats['min'], stats['percentiles']['25'], 
               stats['median'], stats['percentiles']['75'], 
               stats['max']],
            name=lang,
            boxpoints=False
        ))
    
    fig.update_layout(title=title, yaxis_title='Text Length (characters)')
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_html_report(stats: Dict, output_path: str) -> None:
    """Generate an HTML report from cleaning statistics.

    Args:
        stats: Dictionary containing cleaning statistics
        output_path: Path to save the HTML report
    """
    # Create charts
    # Filtering statistics pie chart
    filter_labels = [
        'Empty After Cleaning', 'Too Short', 'Too Long',
        'Word Count Filtered', 'Length Outliers',
        'Domain Outliers', 'Quality Filtered', 'Final Pairs'
    ]
    filter_values = [
        stats['empty_after_cleaning'], stats['too_short'],
        stats['too_long'], stats['word_count_filtered'],
        stats['length_outliers'], stats['domain_outliers'],
        stats['quality_filtered'], stats['final_pairs']
    ]
    filtering_chart = create_pie_chart(filter_labels, filter_values, 'Filtering Results')

    # Length statistics box plot
    length_plot = create_box_plot(stats['length_stats'], 'Text Length Distribution')

    # Load template
    env = Environment(
        loader=PackageLoader('mtcleanse.cleaning', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('report.html')

    # Render template
    html_content = template.render(
        stats=stats,
        filtering_chart=filtering_chart,
        length_plot=length_plot
    )

    # Save report
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding='utf-8') 