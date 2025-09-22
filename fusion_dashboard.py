import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import requests
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Fusion Companies Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cache functions for performance
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data_from_api(api_url):
    """Load JSON data from API endpoint"""
    try:
        # Make GET request to API
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse JSON
        data = response.json()
        return pd.json_normalize(data['companies'])
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error making API request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON response: {str(e)}")
        return None
    except KeyError as e:
        st.error(f"Expected 'companies' key not found in API response: {str(e)}")
        return None
    except Exception as e:
        st.error(f"Unexpected error loading data from API: {str(e)}")
        return None

def main():
    # App title and header
    st.title("Fusion Companies Dashboard")
    st.markdown("*Comprehensive overview of fusion energy companies worldwide*")
    
    # Load data from API automatically on app startup
    api_url = "https://t3zwgehlujggonby.anvil.app/W643GQARK3IPDHVYLUUODAVX/_/api/file/fusion_companies_json"
    
    with st.spinner("Loading fusion companies data..."):
        df = load_data_from_api(api_url)
    
    if df is None or df.empty:
        st.error("Failed to load data from API. Please refresh the page to try again.")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Fuel source filter
    available_fuel_sources = df['fuel_source'].unique().tolist()
    selected_fuel_sources = st.sidebar.multiselect(
        "Fuel Source:",
        options=available_fuel_sources,
        default=available_fuel_sources
    )
    
    # General approach filter
    available_approaches = df['general_approach'].unique().tolist()
    selected_approaches = st.sidebar.multiselect(
        "General Approach:",
        options=available_approaches,
        default=available_approaches
    )
    
    # Apply filters
    filtered_df = df[
        (df['fuel_source'].isin(selected_fuel_sources)) &
        (df['general_approach'].isin(selected_approaches))
    ]
    
    # Main dashboard content - use filtered data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", len(filtered_df))
    
    with col2:
        if not filtered_df.empty:
            total_funding = filtered_df['funding.amount'].sum() / 1e9  # Convert to billions
            st.metric("Total Funding", f"${total_funding:.1f}B")
        else:
            st.metric("Total Funding", "$0B")
    
    with col3:
        if not filtered_df.empty:
            avg_employees = int(filtered_df['employees'].mean())
            st.metric("Avg Employees", f"{avg_employees}")
        else:
            st.metric("Avg Employees", "0")
    
    with col4:
        if not filtered_df.empty:
            avg_output = int(filtered_df['commercial_output.mwe'].mean())
            st.metric("Avg Output", f"{avg_output} MWe")
        else:
            st.metric("Avg Output", "0 MWe")
    
    # Show filter status
    if len(filtered_df) < len(df):
        st.info(f"Showing {len(filtered_df)} of {len(df)} companies based on current filters.")
    
    if filtered_df.empty:
        st.warning("No companies match the selected filters. Please adjust your filter selections.")
        return
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Company Overview", "Analytics", "Detailed Data"])
    
    with tab1:
        st.subheader("Company Profiles")
        
        # Company selection
        selected_company = st.selectbox(
            "Select a company to view details:",
            filtered_df['name'].tolist()
        )
        
        if selected_company:
            company_data = filtered_df[filtered_df['name'] == selected_company].iloc[0]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Description:** {company_data['description']}")
                st.write(f"**Location:** {company_data['location']}")
                st.write(f"**Founded:** {company_data['year_founded'][:4]}")
                st.write(f"**Employees:** {company_data['employees']:,}")
                st.write(f"**Fusion Approach:** {company_data['general_approach']} - {company_data['specific_approach']}")
                st.write(f"**Fuel Source:** {company_data['fuel_source']}")
                st.write(f"**Pilot Plant Timeline:** {company_data['pilot_plant_timeline']}")
            
            with col2:
                funding_millions = company_data['funding.amount'] / 1e6
                st.metric("Total Funding", f"${funding_millions:.0f}M")
                st.metric("Commercial Output", f"{company_data['commercial_output.mwe']} MWe")
                
                # Recent milestones
                st.write("**Recent Milestones:**")
                if isinstance(company_data['milestones_past_12_months'], str):
                    milestones = eval(company_data['milestones_past_12_months'])
                else:
                    milestones = company_data['milestones_past_12_months']
                
                for milestone in milestones:
                    st.write(f"• {milestone}")
    
    with tab2:
        st.subheader("Analytics & Insights")
        
        # Funding distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Funding Distribution by Company**")
            funding_chart = px.bar(
                filtered_df, 
                x='name', 
                y='funding.amount',
                title="Total Funding by Company",
                labels={'funding.amount': 'Funding (USD)', 'name': 'Company'}
            )
            funding_chart.update_xaxes(tickangle=45)
            funding_chart.update_layout(height=400)
            st.plotly_chart(funding_chart, width='stretch')
        
        with col2:
            st.write("**Employee Count vs Commercial Output**")
            scatter_chart = px.scatter(
                filtered_df, 
                x='employees', 
                y='commercial_output.mwe',
                size='funding.amount',
                hover_name='name',
                title="Employees vs Planned Output (bubble size = funding)",
                labels={
                    'employees': 'Number of Employees',
                    'commercial_output.mwe': 'Commercial Output (MWe)'
                }
            )
            scatter_chart.update_layout(height=400)
            st.plotly_chart(scatter_chart, width='stretch')
        
        # Approach distribution
        st.write("**Fusion Approaches**")
        approach_counts = filtered_df['general_approach'].value_counts()
        pie_chart = px.pie(
            values=approach_counts.values, 
            names=approach_counts.index,
            title="Distribution of Fusion Approaches"
        )
        pie_chart.update_layout(height=400, showlegend=True)
        st.plotly_chart(pie_chart, width='stretch')
        
        st.write("**Fuel Sources**")
        fuel_counts = filtered_df['fuel_source'].value_counts()
        fuel_chart = px.bar(
            x=fuel_counts.index,
            y=fuel_counts.values,
            title="Fuel Source Distribution",
            labels={'x': 'Fuel Source', 'y': 'Number of Companies'}
        )
        st.plotly_chart(fuel_chart, width='stretch')
    
    with tab3:
        st.subheader("Complete Company Database")
        
        # Search and additional filter options
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_term = st.text_input("Search companies", placeholder="Enter company name...")
        
        with col2:
            min_funding = st.number_input(
                "Minimum funding (millions USD)",
                min_value=0,
                max_value=int(filtered_df['funding.amount'].max() / 1e6) if not filtered_df.empty else 0,
                value=0
            )
        
        # Apply additional search filters
        final_df = filtered_df.copy()
        
        if search_term:
            final_df = final_df[
                final_df['name'].str.contains(search_term, case=False) |
                final_df['description'].str.contains(search_term, case=False)
            ]
        
        if min_funding > 0:
            final_df = final_df[final_df['funding.amount'] >= min_funding * 1e6]
        
        # Display filtered results
        st.write(f"**Showing {len(final_df)} companies**")
        
        if final_df.empty:
            st.warning("No companies match the current search and filter criteria.")
        else:
            # Select columns to display
            display_columns = [
                'name', 'location', 'year_founded', 'employees', 
                'funding.amount', 'general_approach', 'specific_approach',
                'fuel_source', 'commercial_output.mwe', 'pilot_plant_timeline'
            ]
            
            # Format the dataframe for better display
            display_df = final_df[display_columns].copy()
            display_df['funding.amount'] = display_df['funding.amount'].apply(lambda x: f"${x/1e6:.1f}M")
            display_df['year_founded'] = display_df['year_founded'].apply(lambda x: x[:4])
            
            # Rename columns for better readability
            display_df = display_df.rename(columns={
                'name': 'Company',
                'location': 'Location',
                'year_founded': 'Founded',
                'employees': 'Employees',
                'funding.amount': 'Funding',
                'general_approach': 'General Approach',
                'specific_approach': 'Specific Approach',
                'fuel_source': 'Fuel Source',
                'commercial_output.mwe': 'Output (MWe)',
                'pilot_plant_timeline': 'Pilot Timeline'
            })
            
            st.dataframe(display_df, width='stretch', height=400)

if __name__ == "__main__":
    main()
