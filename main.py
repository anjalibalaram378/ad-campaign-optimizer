import os
from datetime import datetime
from dotenv import load_dotenv
from crew import create_ad_optimizer_crew
from data.public_data_loader import load_campaign_data

# Load environment variables
load_dotenv()


def main():
    """Main entry point for the Multi-Agent Ad Optimizer"""

    print("\n" + "=" * 80)
    print("🚀 MULTI-AGENT AD OPTIMIZER")
    print("=" * 80)
    print("Using 100% FREE PUBLIC DATASETS")
    print("5-Agent CrewAI System + Real Data")
    print("=" * 80 + "\n")

    # Load real campaign data from public sources
    print("STEP 1: Loading data from public datasets...\n")
    campaign_df = load_campaign_data()

    # Convert to list of dicts for agent processing
    campaign_data = campaign_df.to_dict("records")

    # Show data summary
    print("\n" + "=" * 80)
    print("📊 CAMPAIGN DATA LOADED")
    print("=" * 80)
    print(f"Total Campaigns: {len(campaign_data)}")
    print(f"Total Impressions: {campaign_df['impressions'].sum():,.0f}")
    print(f"Total Clicks: {campaign_df['clicks'].sum():,.0f}")
    print(f"Total Conversions: {campaign_df['conversions'].sum():,.0f}")
    print(f"Total Spend: ${campaign_df['spend'].sum():,.2f}")
    print(f"Average CTR: {campaign_df['ctr'].mean():.2f}%")
    print(f"Average CPC: ${campaign_df['cpc'].mean():.2f}")
    print(f"Average ROI: {campaign_df['roi'].mean():.2f}%")
    print("=" * 80 + "\n")

    # Create and run the crew
    print("STEP 2: Initializing Multi-Agent System...\n")
    crew = create_ad_optimizer_crew(campaign_data)

    print("\n" + "=" * 80)
    print("▶️  STARTING CREW EXECUTION")
    print("=" * 80)
    print("This will take a few minutes...\n")

    start_time = datetime.now()

    # Execute the crew
    result = crew.kickoff()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Display results
    print("\n" + "=" * 80)
    print("✅ OPTIMIZATION COMPLETE!")
    print("=" * 80)
    print(f"Execution Time: {duration:.2f} seconds")
    print("=" * 80 + "\n")

    print("📄 FINAL REPORT:\n")
    print(result)
    print("\n" + "=" * 80)

    # Save results
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/optimization_report_{timestamp}.txt"

    with open(filename, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("MULTI-AGENT AD OPTIMIZER - OPTIMIZATION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Execution Time: {duration:.2f} seconds\n")
        f.write(f"Campaigns Analyzed: {len(campaign_data)}\n\n")
        f.write("=" * 80 + "\n")
        f.write("RESULTS\n")
        f.write("=" * 80 + "\n\n")
        f.write(str(result))

    print(f"💾 Report saved: {filename}")
    print("=" * 80 + "\n")

    return result


if __name__ == "__main__":
    main()
