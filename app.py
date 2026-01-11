"""
Root Gradio App for Multi-Agent Ad Optimizer
Calls FastAPI backend via HTTP instead of running crew locally
Designed for deployment on HuggingFace Spaces
"""

import gradio as gr
import json
import sys
import os
from pathlib import Path
import requests

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Configuration
# When deployed to HuggingFace Spaces, set API_URL environment variable
# When running locally, default to localhost
API_URL = os.getenv(
    "API_URL",
    "https://ad-optimizer-148385492360.us-central1.run.app"  # Cloud Run production URL
)

print(f"🌐 API URL: {API_URL}")


def run_optimization(campaign_json):
    """
    Call the FastAPI backend to run optimization
    Instead of running crew locally, makes HTTP request to API

    Args:
        campaign_json: JSON string with campaign data

    Returns:
        str: Formatted optimization results
    """
    try:
        # Parse JSON input
        campaigns = json.loads(campaign_json)

        # Validate it's a list
        if not isinstance(campaigns, list):
            return "❌ Error: Campaign data must be a JSON list\n\nExample:\n[{\"campaign_id\": 1, \"spend\": 1000}]"

        if len(campaigns) == 0:
            return "❌ Error: Provide at least one campaign\n\nExample:\n[{\"campaign_id\": 1, \"spend\": 1000}]"

        # Make HTTP request to FastAPI backend
        print(f"📡 Calling API: {API_URL}/v1/optimize")

        response = requests.post(
            f"{API_URL}/v1/optimize",
            json={"campaigns": campaigns},
            timeout=300  # 5 minute timeout for long-running optimizations
        )

        # Check if request was successful
        if response.status_code != 200:
            return f"❌ API Error ({response.status_code}): {response.text}"

        result = response.json()

        # Format results nicely
        output = "✅ OPTIMIZATION COMPLETE\n\n"
        output += "=" * 50 + "\n"
        output += f"Status: {result.get('status', 'unknown')}\n"
        output += f"Execution Time: {result.get('execution_time', 0):.2f}s\n"
        output += f"Campaigns Analyzed: {result.get('campaigns_analyzed', 0)}\n"
        output += "=" * 50 + "\n\n"
        output += result.get('report', 'No report returned')
        output += "\n" + "=" * 50

        return output

    except json.JSONDecodeError as e:
        return f"❌ JSON Error: {str(e)}\n\nMake sure your input is valid JSON"

    except requests.exceptions.ConnectionError:
        return f"❌ Connection Error: Cannot connect to API at {API_URL}\n\nMake sure the FastAPI backend is running:\n  uvicorn api.app:app --reload"

    except requests.exceptions.Timeout:
        return "❌ Timeout: API took too long to respond (>5 minutes)\n\nTry with fewer or simpler campaigns"

    except Exception as e:
        return f"❌ Error: {str(e)}\n\nCheck that the API is running and all fields are correct"


def create_ui():
    """Create the Gradio interface"""

    # Sample data for users to understand format
    sample_campaigns = [
        {
            "campaign_id": 1,
            "campaign_name": "Google Search Ads",
            "spend": 1000.0,
            "conversions": 50,
            "impressions": 5000,
            "clicks": 250,
            "ctr": 0.05,
            "conversion_rate": 0.20,
            "cpc": 4.0,
            "cpa": 20.0,
            "platform": "Google Ads"
        },
        {
            "campaign_id": 2,
            "campaign_name": "Facebook Ads",
            "spend": 2000.0,
            "conversions": 120,
            "impressions": 8000,
            "clicks": 400,
            "ctr": 0.05,
            "conversion_rate": 0.30,
            "cpc": 5.0,
            "cpa": 16.67,
            "platform": "Facebook Ads"
        }
    ]

    with gr.Blocks(
        title="Multi-Agent Ad Optimizer",
        theme=gr.themes.Soft()
    ) as demo:

        # Header
        gr.Markdown("""
        # 🚀 Multi-Agent Ad Optimizer

        ## Optimize your ad campaigns with AI agents

        This system uses 5 intelligent agents to analyze and optimize your advertising campaigns:
        - **Analytics Agent**: Analyzes campaign performance
        - **Bid Optimizer**: Recommends optimal bids
        - **Budget Manager**: Allocates budget efficiently
        - **Creative Analyzer**: Improves ad creatives
        - **Orchestrator**: Synthesizes all recommendations
        """)

        # API Status
        gr.Markdown(f"""
        ### 🌐 Backend Status
        **API URL**: `{API_URL}`

        Make sure the FastAPI backend is running before clicking optimize!
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # Input section
                gr.Markdown("### 📊 Input Campaign Data")

                input_json = gr.Textbox(
                    label="Campaign Data (JSON format)",
                    placeholder='[{"campaign_id": 1, "spend": 1000, ...}]',
                    lines=15,
                    value=json.dumps(sample_campaigns, indent=2),
                    info="Paste your campaign data as a JSON list"
                )

                gr.Markdown("### 📝 Format Instructions")
                gr.Markdown("""
                Each campaign must have:
                - `campaign_id`: Unique identifier (number)
                - `campaign_name`: Campaign name (string)
                - `spend`: Budget spent (number)
                - `conversions`: Number of conversions (number)
                - `impressions`: Number of impressions (number)
                - `clicks`: Number of clicks (number)
                - `platform`: Ad platform (Google, Facebook, etc.)
                """)

                optimize_btn = gr.Button(
                    "🔥 OPTIMIZE CAMPAIGNS",
                    scale=2,
                    size="lg"
                )

            with gr.Column(scale=1):
                # Output section
                gr.Markdown("### 📈 Optimization Results")

                output = gr.Textbox(
                    label="Optimization Results",
                    lines=20,
                    interactive=False,
                    info="Results from all 5 agents"
                )

        # Example tab
        with gr.Accordion("📚 Example Campaigns"):
            gr.Markdown(f"""
            ```json
            {json.dumps(sample_campaigns, indent=2)}
            ```
            """)

        # Connect button to function
        optimize_btn.click(
            fn=run_optimization,
            inputs=input_json,
            outputs=output
        )

    return demo


if __name__ == "__main__":
    demo = create_ui()

    print("=" * 60)
    print("🚀 Multi-Agent Ad Optimizer UI")
    print("=" * 60)
    print(f"\n📱 Open your browser and go to:")
    print("   👉 http://localhost:7860")
    print(f"\n🌐 Backend API URL: {API_URL}")
    print("\n⏸️  Press Ctrl+C to stop the server\n")

    demo.launch(share=False)
