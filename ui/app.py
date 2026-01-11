import json
import os
import requests
import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/v1/optimize")
TIMEOUT_S = int(os.getenv("OPTIMIZE_TIMEOUT", "300"))

EXAMPLES = {
    "Google Search – Strong Performance": [
        {"campaign_id": 1, "spend": 1000, "conversions": 50, "impressions": 5000, "clicks": 250, "platform": "Google"}
    ],
    "Multi-Platform – Typical Mix": [
        {"campaign_id": 101, "spend": 1200, "conversions": 42, "impressions": 22000, "clicks": 880, "platform": "Google"},
        {"campaign_id": 202, "spend": 900, "conversions": 25, "impressions": 18000, "clicks": 540, "platform": "Meta"},
        {"campaign_id": 303, "spend": 650, "conversions": 18, "impressions": 9000, "clicks": 310, "platform": "LinkedIn"},
    ],
    "Low Conversions – Needs Optimization": [
        {"campaign_id": 11, "spend": 800, "conversions": 2, "impressions": 15000, "clicks": 300, "platform": "Google"},
        {"campaign_id": 12, "spend": 900, "conversions": 1, "impressions": 20000, "clicks": 250, "platform": "Meta"},
    ],
}

DEFAULT_HEADERS = ["campaign_id", "spend", "conversions", "impressions", "clicks", "platform"]


def load_example(name: str):
    df = pd.DataFrame(EXAMPLES[name])
    for col in DEFAULT_HEADERS:
        if col not in df.columns:
            df[col] = None
    return df[DEFAULT_HEADERS]


def _compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    # Safe numeric conversions
    for c in ["spend", "conversions", "impressions", "clicks"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Derived metrics
    df["ctr"] = (df["clicks"] / df["impressions"]).where(df["impressions"] > 0)
    df["cpc"] = (df["spend"] / df["clicks"]).where(df["clicks"] > 0)
    df["cpa"] = (df["spend"] / df["conversions"]).where(df["conversions"] > 0)

    # Round for display
    out = df.copy()
    for c in ["ctr", "cpc", "cpa"]:
        out[c] = out[c].round(4)
    return out


def _plot_spend_vs_conversions(df: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    x = df["spend"].fillna(0)
    y = df["conversions"].fillna(0)
    labels = df["campaign_id"].astype(str)

    ax.scatter(x, y)

    # label points
    for i, txt in enumerate(labels):
        ax.annotate(txt, (x.iloc[i], y.iloc[i]))

    ax.set_xlabel("Spend")
    ax.set_ylabel("Conversions")
    ax.set_title("Spend vs Conversions (by campaign)")
    ax.grid(True, alpha=0.2)
    return fig


def _plot_ctr(df: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    vals = df["ctr"].fillna(0)
    labels = df["campaign_id"].astype(str)

    ax.bar(labels, vals)
    ax.set_xlabel("Campaign ID")
    ax.set_ylabel("CTR")
    ax.set_title("CTR by Campaign")
    ax.grid(True, axis="y", alpha=0.2)
    return fig


def _plot_cpa(df: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    vals = df["cpa"].fillna(0)
    labels = df["campaign_id"].astype(str)

    ax.bar(labels, vals)
    ax.set_xlabel("Campaign ID")
    ax.set_ylabel("CPA")
    ax.set_title("CPA by Campaign")
    ax.grid(True, axis="y", alpha=0.2)
    return fig


def _make_curl(space_base_url: str, payload: dict) -> str:
    # ensure no trailing slash
    base = space_base_url.rstrip("/")
    # For docker spaces, the public app domain is usually ...hf.space
    url = f"{base}/v1/optimize"
    return (
        'curl -X POST "' + url + '" \\\n'
        '  -H "Content-Type: application/json" \\\n'
        "  -d '" + json.dumps(payload) + "'"
    )


def optimize(table: pd.DataFrame, space_url: str):
    if table is None or len(table) == 0:
        return (
            "❌ Please add at least one campaign row.",
            None, None, None,
            pd.DataFrame(),
            {},
            ""
        )

    df = table.copy()

    # Basic required field validation
    for req in ["campaign_id", "spend", "conversions"]:
        if req not in df.columns:
            return (
                f"❌ Missing required column: `{req}`",
                None, None, None,
                pd.DataFrame(),
                {},
                ""
            )

    # Clean metrics table
    metrics_df = _compute_metrics(df)

    # Payload for API
    payload = {"campaigns": df.fillna("").to_dict(orient="records")}

    # Call backend
    try:
        r = requests.post(API_URL, json=payload, timeout=TIMEOUT_S)
        if r.status_code != 200:
            return (
                f"❌ API error {r.status_code}:\n{r.text}",
                None, None, None,
                metrics_df,
                {},
                _make_curl(space_url, payload)
            )
        result = r.json()
    except Exception as e:
        return (
            f"❌ Failed to call backend: {e}",
            None, None, None,
            metrics_df,
            {},
            _make_curl(space_url, payload)
        )

    # Nicely formatted report
    report_md = f"""
## ✅ Optimization Complete

**Campaigns analyzed:** {result.get("campaigns_analyzed", "—")}  
**Execution time:** {float(result.get("execution_time", 0)):.2f}s  
**Timestamp:** {result.get("timestamp", "—")}

---

### 📌 Recommendations Report
{result.get("report","")}
"""

    # Charts
    spend_conv_fig = _plot_spend_vs_conversions(metrics_df)
    ctr_fig = _plot_ctr(metrics_df)
    cpa_fig = _plot_cpa(metrics_df)

    # Return: report, charts, metrics table, raw json, curl
    return (
        report_md,
        spend_conv_fig,
        ctr_fig,
        cpa_fig,
        metrics_df[DEFAULT_HEADERS + ["ctr", "cpc", "cpa"]],
        result,
        _make_curl(space_url, payload)
    )


with gr.Blocks(title="Multi-Agent Ad Campaign Optimizer") as demo:
    gr.Markdown(
        """
# 🚀 Multi-Agent Ad Campaign Optimizer

This demo simulates how **AI agents** optimize ad campaigns across platforms (Google/Meta/LinkedIn).

### What to enter
- **Required:** `campaign_id`, `spend`, `conversions`
- **Helpful (optional):** `impressions`, `clicks`, `platform`

### How to use
1) Load an example (or edit the table)  
2) Click **Optimize Campaigns**  
3) Review **charts + recommendations**
"""
    )

    with gr.Row():
        example_select = gr.Dropdown(choices=list(EXAMPLES.keys()), label="Load example scenario")
        space_url = gr.Textbox(
            label="Your public Space URL (for curl generation)",
            value="https://anjalimahanthi-ad-campaign-optimizer.hf.space",
        )

    campaign_table = gr.Dataframe(
        headers=DEFAULT_HEADERS,
        datatype=["number", "number", "number", "number", "number", "str"],
        label="✏️ Campaign Data (Editable Table)",
        interactive=True,
        value=load_example("Google Search – Strong Performance"),
    )

    example_select.change(load_example, inputs=example_select, outputs=campaign_table)

    optimize_btn = gr.Button("🚀 Optimize Campaigns", variant="primary")

    with gr.Tabs():
        with gr.Tab("Results"):
            report = gr.Markdown(label="Report")
        with gr.Tab("Charts"):
            spend_conv = gr.Plot(label="Spend vs Conversions")
            ctr_plot = gr.Plot(label="CTR by Campaign")
            cpa_plot = gr.Plot(label="CPA by Campaign")
        with gr.Tab("Metrics Table"):
            metrics_table = gr.Dataframe(label="Computed metrics (CTR, CPC, CPA)", interactive=False)
        with gr.Tab("Raw JSON"):
            raw_json = gr.JSON(label="Raw API response")
        with gr.Tab("API Call (curl)"):
            curl_box = gr.Code(label="Copy-paste curl", language="bash")

    optimize_btn.click(
        fn=optimize,
        inputs=[campaign_table, space_url],
        outputs=[report, spend_conv, ctr_plot, cpa_plot, metrics_table, raw_json, curl_box],
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
