import json
import os
import requests
import pandas as pd
import gradio as gr
import matplotlib.pyplot as plt

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/v1/optimize")
TIMEOUT_S = int(os.getenv("OPTIMIZE_TIMEOUT", "300"))

DEFAULT_HEADERS = ["campaign_id", "spend", "conversions", "impressions", "clicks", "platform"]

EXAMPLES = {
    "Google Search – Strong Performance (1 campaign)": [
        {"campaign_id": 1, "spend": 1000, "conversions": 50, "impressions": 5000, "clicks": 250, "platform": "Google"}
    ],
    "Multi-Platform – Typical Mix (3 campaigns)": [
        {"campaign_id": 101, "spend": 1200, "conversions": 42, "impressions": 22000, "clicks": 880, "platform": "Google"},
        {"campaign_id": 202, "spend": 900, "conversions": 25, "impressions": 18000, "clicks": 540, "platform": "Meta"},
        {"campaign_id": 303, "spend": 650, "conversions": 18, "impressions": 9000, "clicks": 310, "platform": "LinkedIn"},
    ],
    "Low Conversions – Needs Optimization (2 campaigns)": [
        {"campaign_id": 11, "spend": 800, "conversions": 2, "impressions": 15000, "clicks": 300, "platform": "Google"},
        {"campaign_id": 12, "spend": 900, "conversions": 1, "impressions": 20000, "clicks": 250, "platform": "Meta"},
    ],
}


def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in DEFAULT_HEADERS:
        if col not in df.columns:
            df[col] = None
    return df[DEFAULT_HEADERS]


def _compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ["spend", "conversions", "impressions", "clicks"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["ctr"] = (df["clicks"] / df["impressions"]).where(df["impressions"] > 0)
    df["cpc"] = (df["spend"] / df["clicks"]).where(df["clicks"] > 0)
    df["cpa"] = (df["spend"] / df["conversions"]).where(df["conversions"] > 0)

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
    base = space_base_url.rstrip("/")
    url = f"{base}/v1/optimize"
    return (
        f'curl -X POST "{url}" \\\n'
        f'  -H "Content-Type: application/json" \\\n'
        f"  -d '{json.dumps(payload)}'"
    )


def load_example(name: str):
    campaigns = EXAMPLES[name]
    df = _normalize_df(pd.DataFrame(campaigns))
    json_text = json.dumps({"campaigns": campaigns}, indent=2)
    return df, json_text


def table_to_json(table: pd.DataFrame):
    if table is None or len(table) == 0:
        return json.dumps({"campaigns": []}, indent=2)
    df = _normalize_df(table)
    payload = {"campaigns": df.fillna("").to_dict(orient="records")}
    return json.dumps(payload, indent=2)


def json_to_table(json_text: str):
    obj = json.loads(json_text)
    campaigns = obj.get("campaigns", [])
    df = _normalize_df(pd.DataFrame(campaigns))
    return df


def optimize_from_payload(payload: dict, space_url: str, df_for_charts: pd.DataFrame):
    # Call backend
    try:
        r = requests.post(API_URL, json=payload, timeout=TIMEOUT_S)
        if r.status_code != 200:
            return (
                f"❌ API error {r.status_code}:\n{r.text}",
                None, None, None,
                pd.DataFrame(),
                {},
                _make_curl(space_url, payload)
            )
        result = r.json()
    except Exception as e:
        return (
            f"❌ Failed to call backend: {e}",
            None, None, None,
            pd.DataFrame(),
            {},
            _make_curl(space_url, payload)
        )

    # report
    report_md = f"""
## ✅ Optimization Complete

**Campaigns analyzed:** {result.get("campaigns_analyzed", "—")}  
**Execution time:** {float(result.get("execution_time", 0)):.2f}s  
**Timestamp:** {result.get("timestamp", "—")}

---

### 📌 Recommendations Report
{result.get("report","")}
"""

    metrics_df = _compute_metrics(df_for_charts)

    spend_conv_fig = _plot_spend_vs_conversions(metrics_df)
    ctr_fig = _plot_ctr(metrics_df)
    cpa_fig = _plot_cpa(metrics_df)

    return (
        report_md,
        spend_conv_fig,
        ctr_fig,
        cpa_fig,
        metrics_df[DEFAULT_HEADERS + ["ctr", "cpc", "cpa"]],
        result,
        _make_curl(space_url, payload)
    )


def optimize_table(table: pd.DataFrame, space_url: str):
    if table is None or len(table) == 0:
        return "❌ Add at least 1 campaign row.", None, None, None, pd.DataFrame(), {}, ""

    df = _normalize_df(table)
    payload = {"campaigns": df.fillna("").to_dict(orient="records")}
    return optimize_from_payload(payload, space_url, df)


def optimize_json(json_text: str, space_url: str):
    try:
        obj = json.loads(json_text)
    except Exception as e:
        return f"❌ Invalid JSON: {e}", None, None, None, pd.DataFrame(), {}, ""

    if "campaigns" not in obj or not isinstance(obj["campaigns"], list) or len(obj["campaigns"]) == 0:
        return "❌ JSON must contain: {\"campaigns\": [ ... ]} with at least 1 campaign.", None, None, None, pd.DataFrame(), {}, ""

    df = _normalize_df(pd.DataFrame(obj["campaigns"]))
    payload = {"campaigns": df.fillna("").to_dict(orient="records")}
    return optimize_from_payload(payload, space_url, df)


with gr.Blocks(title="Multi-Agent Ad Campaign Optimizer") as demo:
    gr.Markdown("""
# 🚀 Multi-Agent Ad Campaign Optimizer

### Use either mode:
- **Table mode** (easy)
- **JSON mode** (paste multiple campaigns)

**Required fields:** `campaign_id`, `spend`, `conversions`  
**Optional:** `impressions`, `clicks`, `platform`
""")

    with gr.Row():
        example_select = gr.Dropdown(choices=list(EXAMPLES.keys()), label="Load example scenario")
        space_url = gr.Textbox(
            label="Your public Space URL (for curl generation)",
            value="https://anjalimahanthi-ad-campaign-optimizer.hf.space",
        )

    with gr.Tabs():
        with gr.Tab("✅ Table Input"):
            campaign_table = gr.Dataframe(
                headers=DEFAULT_HEADERS,
                datatype=["number", "number", "number", "number", "number", "str"],
                label="Campaign Data (Editable Table)",
                interactive=True,
            )
            sync_to_json_btn = gr.Button("↔️ Update JSON from Table")

        with gr.Tab("🧾 JSON Input (paste multiple campaigns)"):
            campaign_json = gr.Code(
                label="Campaign JSON (supports multiple campaigns)",
                language="json",
                value=json.dumps({"campaigns": EXAMPLES["Multi-Platform – Typical Mix (3 campaigns)"]}, indent=2),
            )
            sync_to_table_btn = gr.Button("↔️ Update Table from JSON")

    optimize_btn = gr.Button("🚀 Optimize Campaigns", variant="primary")

    with gr.Tabs():
        with gr.Tab("Results"):
            report = gr.Markdown()
        with gr.Tab("Charts"):
            spend_conv = gr.Plot()
            ctr_plot = gr.Plot()
            cpa_plot = gr.Plot()
        with gr.Tab("Metrics Table"):
            metrics_table = gr.Dataframe(interactive=False)
        with gr.Tab("Raw JSON"):
            raw_json = gr.JSON()
        with gr.Tab("API Call (curl)"):
            curl_box = gr.Code(label="Copy-paste curl", language="shell")

    # Example loads both
    example_select.change(load_example, inputs=example_select, outputs=[campaign_table, campaign_json])

    # Sync buttons
    sync_to_json_btn.click(table_to_json, inputs=campaign_table, outputs=campaign_json)
    sync_to_table_btn.click(json_to_table, inputs=campaign_json, outputs=campaign_table)

    # Optimize: uses JSON tab content (always accurate for multi-campaign),
    # but keeps table in sync so charts/metrics work.
    optimize_btn.click(
        fn=optimize_json,
        inputs=[campaign_json, space_url],
        outputs=[report, spend_conv, ctr_plot, cpa_plot, metrics_table, raw_json, curl_box],
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
