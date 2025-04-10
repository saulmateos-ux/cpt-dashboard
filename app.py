import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_code import data  # Import the actual data

# Set style for better visualization
plt.style.use('bmh')  # Using a built-in matplotlib style
sns.set_palette("husl")

# Title
st.title("CPT Code Financial Dashboard by Partner")

# Create the DataFrame directly from the imported data
df = pd.DataFrame(data)

# Column mapping with predefined selections (hidden from UI)
partner_col = "Partner Account"
cpt_col = "CPT Code 1"
repaid_col = "Total Amounts Repaid 1 + 2"
invoice_col = "Invoice Amount"
medicare_col = "Medicare"
medicaid_col = "Medicaid"
description_col = "Description"

try:
    processed_df = df.copy()
    processed_df = processed_df.rename(columns={
        partner_col: "Partner",
        cpt_col: "CPT_Code",
        repaid_col: "Repaid",
        invoice_col: "Invoice",
        medicare_col: "Medicare",
        medicaid_col: "Medicaid",
        description_col: "Description"
    })

    # Drop rows with missing CPT codes or Partner names
    processed_df = processed_df[processed_df["CPT_Code"].notnull() & processed_df["Partner"].notnull()]
    
    # Filter for rows that have either Medicare or Medicaid data
    processed_df = processed_df[
        (processed_df["Medicare"] > 0) | (processed_df["Medicaid"] > 0)
    ]

    # Calculate provider totals for the top 10 summary
    provider_totals = processed_df.groupby("Partner").agg({
        "Invoice": "sum",
        "Repaid": "sum"
    }).reset_index()
    
    # Calculate repaid percentage
    provider_totals["Repaid_Percentage"] = (provider_totals["Repaid"] / provider_totals["Invoice"] * 100).round(1)
    
    # Sort by Invoice amount and get top 10
    top_10_providers = provider_totals.nlargest(10, "Invoice")
    
    # Display top 10 providers summary
    st.subheader("Top 10 Georgia Providers by Total Invoice Amount")
    
    # Format the data for display
    top_10_providers_display = top_10_providers.copy()
    top_10_providers_display["Invoice"] = top_10_providers_display["Invoice"].apply(lambda x: f"${x:,.2f}")
    top_10_providers_display["Repaid"] = top_10_providers_display["Repaid"].apply(lambda x: f"${x:,.2f}")
    top_10_providers_display["Repaid_Percentage"] = top_10_providers_display["Repaid_Percentage"].apply(lambda x: f"{x}%")
    
    # Rename columns for display
    top_10_providers_display = top_10_providers_display.rename(columns={
        "Partner": "Provider",
        "Invoice": "Total Invoice",
        "Repaid": "Total Repaid",
        "Repaid_Percentage": "Repaid %"
    })
    
    st.dataframe(
        top_10_providers_display,
        use_container_width=True
    )
    
    st.markdown("---")  # Add a divider

    # Group by Partner + CPT code and calculate averages
    agg_df = processed_df.groupby(["Partner", "CPT_Code"]).agg({
        "Description": "first",
        "Invoice": "mean",
        "Repaid": "mean",
        "Medicare": "mean",
        "Medicaid": "mean"
    }).reset_index()

    # Round for cleaner display
    agg_df = agg_df.round(2)

    # Partner selection
    partner_list = agg_df["Partner"].sort_values().unique()
    selected_partner = st.selectbox("Select a Healthcare Provider (Partner):", partner_list)

    # Filter data by selected partner
    filtered_df = agg_df[agg_df["Partner"] == selected_partner]
    
    # Sort by Invoice amount and get total number of CPT codes
    filtered_df = filtered_df.sort_values("Invoice", ascending=False)
    total_cpt_codes = len(filtered_df)
    
    # Add slider for selecting number of CPT codes to display
    num_codes = st.slider("Number of CPT codes to display", 
                        min_value=1, 
                        max_value=total_cpt_codes, 
                        value=min(10, total_cpt_codes),
                        help="Select how many CPT codes to show, sorted by highest Invoice amount")
    
    # Filter to selected number of codes
    display_df = filtered_df.head(num_codes)

    # Display metrics table
    st.subheader(f"Top {num_codes} CPT Metrics for {selected_partner} (by Invoice Amount)")
    st.dataframe(
        display_df[["CPT_Code", "Description", "Invoice", "Repaid", "Medicare", "Medicaid"]],
        use_container_width=True
    )

    # Plotting averages per CPT code
    st.subheader("Financial Averages by CPT Code")
    plot_data = display_df.set_index("CPT_Code")[["Invoice", "Repaid", "Medicare", "Medicaid"]]

    # Column chart with improved styling
    fig, ax = plt.subplots(figsize=(12, 6))
    bar_width = 0.2
    index = range(len(plot_data.index))
    
    # Plot bars with offset and custom colors
    colors = sns.color_palette("husl", 4)
    ax.bar(index, plot_data["Invoice"], bar_width, label="Invoice", color=colors[0], alpha=0.8)
    ax.bar([i + bar_width for i in index], plot_data["Repaid"], bar_width, label="Repaid", color=colors[1], alpha=0.8)
    ax.bar([i + bar_width * 2 for i in index], plot_data["Medicare"], bar_width, label="Medicare", color=colors[2], alpha=0.8)
    ax.bar([i + bar_width * 3 for i in index], plot_data["Medicaid"], bar_width, label="Medicaid", color=colors[3], alpha=0.8)

    # Customize chart
    ax.set_ylabel("Average Amount ($)", fontsize=12)
    ax.set_title(f"Average Financial Metrics - {selected_partner}\n(Top {num_codes} CPT Codes by Invoice Amount)", 
                fontsize=14, pad=20)
    ax.set_xticks([i + bar_width * 1.5 for i in index])
    ax.set_xticklabels(plot_data.index, rotation=45, ha='right')
    
    # Add grid for better readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    ax.set_axisbelow(True)
    
    # Add legend
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    st.pyplot(fig)

    # New chart with averages and percentages
    st.subheader("Average Amounts and Recovery Percentages")
    
    # Calculate averages
    avg_invoice = display_df['Invoice'].mean()
    avg_repaid = display_df['Repaid'].mean()
    avg_combined = (display_df['Invoice'].mean() + display_df['Medicare'].mean() + display_df['Medicaid'].mean()) / 3
    
    # Calculate percentages
    pct_repaid = (avg_repaid / avg_invoice * 100) if avg_invoice > 0 else 0
    pct_combined = (avg_combined / avg_invoice * 100) if avg_invoice > 0 else 0

    # Create figure with two y-axes
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    # Plot bars for averages
    x = ['Invoice', 'Repaid', 'Avg(Invoice,\nMedicare,Medicaid)']
    averages = [avg_invoice, avg_repaid, avg_combined]
    bars = ax1.bar([0, 1, 2], averages, width=0.4, alpha=0.6, color=sns.color_palette("husl", 3))
    
    # Plot lines for percentages
    ax2.plot([1], [pct_repaid], 'ro-', label='Repaid %', linewidth=2, markersize=10)
    ax2.plot([2], [pct_combined], 'go-', label='Combined %', linewidth=2, markersize=10)

    # Customize axes
    ax1.set_ylabel('Average Amount ($)', color='black')
    ax2.set_ylabel('Percentage of Invoice (%)', color='black')
    ax1.set_xticks([0, 1, 2])
    ax1.set_xticklabels(x)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:,.0f}',
                ha='center', va='bottom')

    # Add percentage labels
    ax2.text(1, pct_repaid, f'{pct_repaid:.1f}%', ha='center', va='bottom')
    ax2.text(2, pct_combined, f'{pct_combined:.1f}%', ha='center', va='bottom')

    # Add grid and legend
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.set_axisbelow(True)
    
    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')

    plt.title(f'Average Amounts and Recovery Percentages - {selected_partner}')
    plt.tight_layout()
    st.pyplot(fig)

    # Calculate true totals from the filtered processed_df for the selected partner
    partner_data = processed_df[processed_df["Partner"] == selected_partner]
    partner_totals = partner_data.agg({
        "Invoice": "sum",
        "Repaid": "sum",
        "Medicare": "sum",
        "Medicaid": "sum"
    })
    
    total_invoice = partner_totals['Invoice']
    total_repaid = partner_totals['Repaid']
    total_medicare = partner_totals['Medicare']
    total_medicaid = partner_totals['Medicaid']
    
    repaid_pct = (total_repaid / total_invoice * 100) if total_invoice > 0 else 0
    medicare_pct = (total_medicare / total_invoice * 100) if total_invoice > 0 else 0
    medicaid_pct = (total_medicaid / total_invoice * 100) if total_invoice > 0 else 0

    # Add summary statistics with percentages
    st.subheader("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Invoice Amount", f"${total_invoice:,.2f}")
    with col2:
        st.metric("Total Repaid Amount", f"${total_repaid:,.2f}", f"{repaid_pct:.1f}% of Invoice")
    with col3:
        st.metric("Total Medicare", f"${total_medicare:,.2f}", f"{medicare_pct:.1f}% of Invoice")
    with col4:
        st.metric("Total Medicaid", f"${total_medicaid:,.2f}", f"{medicaid_pct:.1f}% of Invoice")

    st.markdown("---")  # Add a divider

    # Add MOIC Analysis section
    st.subheader("MOIC Analysis")
    
    # Add slider for advance percentage
    advance_pct = st.slider("Select Invoice Advance Percentage", 
                          min_value=0, 
                          max_value=100, 
                          value=70,
                          help="Percentage of invoice amount advanced to the provider")

    # Convert advance percentage to decimal
    advance_decimal = advance_pct / 100.0

    # Calculate the amount advanced
    amount_advanced = total_invoice * advance_decimal

    # Calculate Current MOIC
    current_moic = total_repaid / amount_advanced if amount_advanced > 0 else 0
    
    # Calculate Estimated MOIC (based on average of total potential recovery)
    potential_recovery = (total_invoice + total_medicare + total_medicaid) / 3  # Average of the three values
    estimated_moic = potential_recovery / amount_advanced if amount_advanced > 0 else 0

    # Display MOIC metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Amount Advanced", f"${amount_advanced:,.2f}", f"{advance_pct}% of Invoice")
    with col2:
        st.metric("Current MOIC", 
                 f"{current_moic:.2f}x", 
                 f"Based on ${total_repaid:,.2f} repaid")
    with col3:
        st.metric("Estimated MOIC", 
                 f"{estimated_moic:.2f}x", 
                 f"Based on ${potential_recovery:,.2f} potential")

    # Add explanation
    st.info("""
    **MOIC Calculation:**
    - Amount Advanced = Total Invoice × Advance %
    - Current MOIC = Total Repaid ÷ Amount Advanced
    - Estimated MOIC = Average(Invoice + Medicare + Medicaid) ÷ Amount Advanced
    """)

except Exception as e:
    st.error(f"Error processing data: {str(e)}")
    st.info("Please make sure the Excel file contains the required columns.") 