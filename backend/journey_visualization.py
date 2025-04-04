"""
Journey Visualization Module for RBC Mortgage & Creditor Insurance Advisor Assistant
Provides tools for visualizing the mortgage journey and protection discussion opportunities
"""
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta

from backend.mortgage_journey import (
    MortgageJourney,
    MortgageJourneyStage,
    ProtectionDiscussionStatus,
    get_journey_stage_description
)

def create_journey_timeline(journey: MortgageJourney) -> go.Figure:
    """
    Create an interactive timeline visualization of a client's mortgage journey
    with protection discussion opportunities highlighted
    """
    # Get all stages in order
    all_stages = list(MortgageJourneyStage)
    
    # Prepare data for timeline
    stages = []
    start_dates = []
    end_dates = []
    colors = []
    hover_texts = []
    
    current_stage_index = all_stages.index(journey.current_stage)
    
    # Add past and current stages
    for i, stage in enumerate(all_stages[:current_stage_index + 1]):
        stage_info = get_journey_stage_description(stage)
        stage_name = stage_info.get("name", stage.value)
        
        # Get actual start date from history or estimate
        if stage in journey.stage_history:
            start_date = journey.stage_history[stage]
        else:
            # Estimate based on journey start date
            days_offset = i * 3  # Simple estimation
            start_date = journey.started_at + timedelta(days=days_offset)
        
        # Get end date (either next stage start or current date)
        if i < current_stage_index:
            next_stage = all_stages[i + 1]
            if next_stage in journey.stage_history:
                end_date = journey.stage_history[next_stage]
            else:
                end_date = start_date + timedelta(days=3)  # Simple estimation
        else:
            # Current stage
            end_date = datetime.now()
        
        # Determine color based on protection discussion status
        if stage == journey.current_stage:
            color = "rgba(254, 223, 1, 0.8)"  # RBC Yellow for current stage
        elif journey.protection_discussion != ProtectionDiscussionStatus.NOT_DISCUSSED and \
             journey.protection_discussion_date and \
             start_date <= journey.protection_discussion_date <= end_date:
            color = "rgba(0, 66, 178, 0.8)"  # RBC Blue for stages with protection discussion
        else:
            color = "rgba(150, 150, 150, 0.6)"  # Grey for other completed stages
        
        # Create hover text with stage info and protection status
        protection_text = ""
        if journey.protection_discussion != ProtectionDiscussionStatus.NOT_DISCUSSED and \
           journey.protection_discussion_date and \
           start_date <= journey.protection_discussion_date <= end_date:
            protection_text = f"<br><b>Protection discussed:</b> {journey.protection_discussion.value.replace('_', ' ').title()}"
        
        hover_text = f"<b>{stage_name}</b><br>" + \
                     f"Start: {start_date.strftime('%Y-%m-%d')}<br>" + \
                     f"End: {end_date.strftime('%Y-%m-%d')}" + \
                     protection_text
        
        stages.append(stage_name)
        start_dates.append(start_date)
        end_dates.append(end_date)
        colors.append(color)
        hover_texts.append(hover_text)
    
    # Add future stages with estimated dates
    for i, stage in enumerate(all_stages[current_stage_index + 1:], start=current_stage_index + 1):
        stage_info = get_journey_stage_description(stage)
        stage_name = stage_info.get("name", stage.value)
        
        # Estimate dates
        typical_duration = stage_info.get("typical_duration", "3-7 days")
        # Extract average days from typical duration format like "3-7 days"
        try:
            days_range = typical_duration.split(" ")[0].split("-")
            avg_days = (int(days_range[0]) + int(days_range[1])) / 2
        except:
            avg_days = 5  # Default if parsing fails
        
        start_date = end_dates[-1]
        end_date = start_date + timedelta(days=avg_days)
        
        stages.append(stage_name)
        start_dates.append(start_date)
        end_dates.append(end_date)
        colors.append("rgba(220, 220, 220, 0.3)")  # Light grey for future stages
        
        hover_text = f"<b>{stage_name}</b> (Upcoming)<br>" + \
                     f"Estimated start: {start_date.strftime('%Y-%m-%d')}<br>" + \
                     f"Estimated duration: {typical_duration}"
        hover_texts.append(hover_text)
    
    # Create a simpler timeline visualization that avoids datetime serialization issues
    # Convert datetime objects to strings for JSON serialization
    start_dates_str = [date.strftime('%Y-%m-%d') for date in start_dates]
    end_dates_str = [date.strftime('%Y-%m-%d') for date in end_dates]
    
    # Calculate durations in days for bar lengths
    durations = [(end - start).days for start, end in zip(start_dates, end_dates)]
    # Ensure minimum duration of 1 day for visibility
    durations = [max(1, d) for d in durations]
    
    # Create the timeline visualization with a different approach
    fig = go.Figure()
    
    # Create better display names for stages (capitalize and replace underscores)
    stages_display = [stage.replace('_', ' ').title() if '_' in stage else stage for stage in stages]
    
    # Add horizontal bars for each stage with improved styling
    for i in range(len(stages)):
        fig.add_trace(go.Bar(
            y=[stages_display[i]],  # Use the more readable display names
            x=[durations[i]],
            orientation='h',
            marker=dict(
                color=colors[i],
                line=dict(width=1, color='rgba(0,0,0,0.3)')  # Add border to bars for better visibility
            ),
            hoverinfo='text',
            hovertext=hover_texts[i],
            name=stages_display[i],
            showlegend=False
        ))
    
    # Add protection opportunity markers
    optimal_stage = journey.get_optimal_protection_discussion_stage()
    optimal_stage_info = get_journey_stage_description(optimal_stage)
    optimal_stage_name = optimal_stage_info.get("name", optimal_stage.value)
    
    # Find the index of the optimal stage
    if optimal_stage_name in stages:
        optimal_index = stages.index(optimal_stage_name)
        # Create display name for the optimal stage
        optimal_stage_display = optimal_stage_name.replace('_', ' ').title() if '_' in optimal_stage_name else optimal_stage_name
        # Place marker at middle of the bar
        marker_position = durations[optimal_index] / 2
        
        fig.add_trace(go.Scatter(
            x=[marker_position],
            y=[stages_display[optimal_index]],  # Use the display name here
            mode='markers',
            marker=dict(
                symbol='star',
                size=18,  # Slightly larger for better visibility
                color='#FEDF01',  # RBC Yellow
                line=dict(color='#0042B2', width=2)  # RBC Blue border
            ),
            name='Optimal Protection Discussion',
            hoverinfo='text',
            hovertext=f"<b>Optimal time to discuss protection</b><br>Stage: {optimal_stage_display}"
        ))
    
    # Add current date annotation instead of a marker
    # This avoids datetime serialization issues
    now = datetime.now()
    
    # Add annotation for current date with improved styling
    fig.add_annotation(
        x=0,
        y=1.08,
        xref="paper",
        yref="paper",
        text=f"<b>Current Date:</b> {now.strftime('%Y-%m-%d')}",
        showarrow=False,
        font=dict(color="#0042B2", size=12),
        bgcolor="#FFFFFF",
        bordercolor="#0042B2",
        borderwidth=1,
        borderpad=4,
        align="left"
    )
    
    # Add stage progress indicator
    current_stage_display = stages_display[current_stage_index]
    fig.add_annotation(
        x=1,
        y=1.08,
        xref="paper",
        yref="paper",
        text=f"<b>Current Stage:</b> {current_stage_display} ({current_stage_index + 1}/{len(stages)})",
        showarrow=False,
        font=dict(color="#0042B2", size=12),
        bgcolor="#FFFFFF",
        bordercolor="#0042B2",
        borderwidth=1,
        borderpad=4,
        align="right"
    )
    
    # Customize layout with improved styling
    fig.update_layout(
        title={
            "text": "Mortgage Journey Timeline",
            "font": {"size": 18, "color": "#0042B2"},
            "y": 0.95
        },
        xaxis=dict(
            title="Duration (days)",
            tickangle=0,
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.2)"
        ),
        yaxis=dict(
            title=None,  # Remove y-axis title to reduce clutter
            autorange="reversed",  # Show stages in chronological order from top to bottom
            showgrid=True,
            gridcolor="rgba(200, 200, 200, 0.2)"
        ),
        height=400,
        margin=dict(l=10, r=10, t=60, b=10),
        plot_bgcolor="rgba(255, 255, 255, 0.95)",
        paper_bgcolor="rgba(255, 255, 255, 0.95)",
        hovermode="closest",
        bargap=0.2,  # Gap between bars
        shapes=[{
            "type": "rect",
            "xref": "paper",
            "yref": "paper",
            "x0": 0,
            "y0": 0,
            "x1": 1,
            "y1": 1,
            "line": {"width": 2, "color": "#0042B2"},
            "fillcolor": "rgba(0, 0, 0, 0)"
        }]
    )
    
    return fig

def create_protection_opportunity_gauge(
    journey: MortgageJourney,
    client_data: Dict[str, Any]
) -> go.Figure:
    """
    Create a gauge visualization showing the current protection opportunity level
    based on journey stage, client profile, and other factors
    """
    # Calculate opportunity score (0-100)
    score = 50  # Default middle value
    
    # Adjust based on journey stage
    optimal_stage = journey.get_optimal_protection_discussion_stage()
    current_stage_idx = list(MortgageJourneyStage).index(journey.current_stage)
    optimal_stage_idx = list(MortgageJourneyStage).index(optimal_stage)
    
    # Highest score when at optimal stage
    if journey.current_stage == optimal_stage:
        score += 30
    # Decreasing score as we move away from optimal stage
    elif current_stage_idx < optimal_stage_idx:
        # Before optimal stage
        distance = optimal_stage_idx - current_stage_idx
        score += max(0, 20 - distance * 10)
    else:
        # After optimal stage
        distance = current_stage_idx - optimal_stage_idx
        score += max(0, 20 - distance * 5)
    
    # Adjust based on protection discussion status
    if journey.protection_discussion == ProtectionDiscussionStatus.NOT_DISCUSSED:
        score += 10  # Opportunity to start discussion
    elif journey.protection_discussion == ProtectionDiscussionStatus.BRIEFLY_MENTIONED:
        score += 15  # Good opportunity to follow up
    elif journey.protection_discussion == ProtectionDiscussionStatus.DETAILED_DISCUSSION:
        score += 5  # Some opportunity to follow up
    elif journey.protection_discussion == ProtectionDiscussionStatus.CLIENT_INTERESTED:
        score += 20  # Strong opportunity to close
    elif journey.protection_discussion == ProtectionDiscussionStatus.CLIENT_DECLINED:
        score -= 30  # Lower opportunity if client declined
    
    # Adjust based on client risk factors
    if client_data.get("dependents", 0) > 0:
        score += 5 * min(client_data.get("dependents", 0), 3)  # Up to +15 for dependents
    
    if client_data.get("mortgage_amount", 0) > client_data.get("annual_income", 0) * 3:
        score += 10  # Higher score for high mortgage-to-income ratio
    
    # Cap score between 0 and 100
    score = max(0, min(100, score))
    
    # Determine opportunity level and color
    if score >= 75:
        opportunity_level = "High"
        color = "#00B050"  # Green
    elif score >= 40:
        opportunity_level = "Medium"
        color = "#FEDF01"  # RBC Yellow
    else:
        opportunity_level = "Low"
        color = "#FF0000"  # Red
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Protection Opportunity: {opportunity_level}"},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': color},
            'steps': [
                {'range': [0, 40], 'color': 'rgba(255, 0, 0, 0.2)'},
                {'range': [40, 75], 'color': 'rgba(254, 223, 1, 0.2)'},
                {'range': [75, 100], 'color': 'rgba(0, 176, 80, 0.2)'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(255, 255, 255, 0.9)',
        paper_bgcolor='rgba(255, 255, 255, 0.9)'
    )
    
    return fig

def create_protection_impact_chart(
    client_data: Dict[str, Any],
    scenario_type: str = "disability"
) -> go.Figure:
    """
    Create a chart showing the financial impact of different scenarios
    with and without protection
    """
    # Get relevant client data
    mortgage_amount = client_data.get("mortgage_amount", 300000)
    monthly_payment = client_data.get("monthly_payment", 1500)
    annual_income = client_data.get("annual_income", 75000)
    monthly_income = annual_income / 12
    
    # Calculate basic monthly expenses (estimated)
    monthly_expenses = monthly_income * 0.7  # Assumption: 70% of income goes to expenses
    
    # Scenario parameters
    if scenario_type == "disability":
        duration_months = 6
        income_reduction = 0.4  # 40% of income lost
        with_protection_coverage = 0.8  # 80% of mortgage payment covered
    elif scenario_type == "critical_illness":
        duration_months = 12
        income_reduction = 0.6  # 60% of income lost
        with_protection_coverage = 1.0  # 100% of mortgage payment covered (lump sum)
    elif scenario_type == "job_loss":
        duration_months = 3
        income_reduction = 1.0  # 100% of income lost
        with_protection_coverage = 0.6  # 60% of mortgage payment covered
    elif scenario_type == "death":
        duration_months = 24  # Looking at longer-term impact
        income_reduction = 1.0  # 100% of primary income lost
        with_protection_coverage = 1.0  # 100% of mortgage paid off
    else:
        # Default to disability scenario
        duration_months = 6
        income_reduction = 0.4
        with_protection_coverage = 0.8
    
    # Calculate financial impact
    months = list(range(1, duration_months + 1))
    
    # Without protection
    income_without_protection = [monthly_income * (1 - income_reduction) for _ in months]
    expenses_without_protection = [monthly_expenses for _ in months]
    mortgage_without_protection = [monthly_payment for _ in months]
    
    balance_without_protection = [
        income - expenses - mortgage 
        for income, expenses, mortgage in zip(
            income_without_protection, 
            expenses_without_protection, 
            mortgage_without_protection
        )
    ]
    
    cumulative_balance_without = []
    current_balance = 0
    for monthly_balance in balance_without_protection:
        current_balance += monthly_balance
        cumulative_balance_without.append(current_balance)
    
    # With protection
    income_with_protection = income_without_protection.copy()
    expenses_with_protection = expenses_without_protection.copy()
    
    if scenario_type == "death":
        # Mortgage is paid off
        mortgage_with_protection = [0 for _ in months]
    else:
        # Partial coverage of mortgage
        mortgage_with_protection = [
            monthly_payment * (1 - with_protection_coverage) for _ in months
        ]
    
    balance_with_protection = [
        income - expenses - mortgage 
        for income, expenses, mortgage in zip(
            income_with_protection, 
            expenses_with_protection, 
            mortgage_with_protection
        )
    ]
    
    cumulative_balance_with = []
    current_balance = 0
    for monthly_balance in balance_with_protection:
        current_balance += monthly_balance
        cumulative_balance_with.append(current_balance)
    
    # Create the chart
    fig = go.Figure()
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_balance_without,
        mode='lines+markers',
        name='Without Protection',
        line=dict(color='#FF0000', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=months,
        y=cumulative_balance_with,
        mode='lines+markers',
        name='With Protection',
        line=dict(color='#00B050', width=3),
        marker=dict(size=8)
    ))
    
    # Add zero line
    fig.add_hline(
        y=0,
        line_width=1,
        line_dash="dash",
        line_color="gray"
    )
    
    # Customize layout
    scenario_titles = {
        "disability": f"Financial Impact of Disability ({duration_months} months)",
        "critical_illness": f"Financial Impact of Critical Illness ({duration_months} months)",
        "job_loss": f"Financial Impact of Job Loss ({duration_months} months)",
        "death": f"Financial Impact of Death on Family ({duration_months} months)"
    }
    
    fig.update_layout(
        title=scenario_titles.get(scenario_type, f"Financial Impact Scenario ({duration_months} months)"),
        xaxis=dict(
            title="Month",
            tickmode='linear',
            tick0=1,
            dtick=1
        ),
        yaxis=dict(
            title="Cumulative Financial Impact ($)",
            tickprefix="$",
            tickformat=",."
        ),
        height=400,
        margin=dict(l=10, r=10, t=50, b=10),
        plot_bgcolor='rgba(255, 255, 255, 0.9)',
        paper_bgcolor='rgba(255, 255, 255, 0.9)',
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add annotations for key insights
    protection_benefit = cumulative_balance_with[-1] - cumulative_balance_without[-1]
    
    fig.add_annotation(
        x=duration_months,
        y=cumulative_balance_without[-1],
        text=f"${cumulative_balance_without[-1]:,.2f}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )
    
    fig.add_annotation(
        x=duration_months,
        y=cumulative_balance_with[-1],
        text=f"${cumulative_balance_with[-1]:,.2f}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=40
    )
    
    fig.add_annotation(
        x=duration_months / 2,
        y=(cumulative_balance_with[-1] + cumulative_balance_without[-1]) / 2,
        text=f"Protection Benefit: ${protection_benefit:,.2f}",
        showarrow=False,
        bgcolor="#FEDF01",
        bordercolor="#0042B2",
        borderwidth=2,
        borderpad=4
    )
    
    return fig
