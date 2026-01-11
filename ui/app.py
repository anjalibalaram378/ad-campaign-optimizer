import json
import os
import requests
import gradio as gr

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/v1/optimize")

DEFAULT_JSON = {
    "campaigns": [
        {
            "campaign_id": 1,
            "spend": 1000,
            "conversions": 50,
            "impressions": 5000,
            "clicks": 250,
            "platform": "Google"
        }
    ]
}


def optimize(json_text: str):
    # 1) Parse JSON
    try:
        payload = json.loads(json_text)
    except Exception as e:
        return f"❌ Invalid JSON: {e}"

    # 2) Call FastAPI backend
    try:
        r = requests.post(API_URL, json=payload, timeout=300)
        if r.status_code != 200:
            return f"❌ API error {r.status_code}:\n{r.text}"
        data = r.json()
    except Exception as e:
        return f"❌ Failed to call backend: {e}"

    # 3) Pretty print result
    return json.dumps(data, indent=2)


with gr.Blocks(title="Ad Campaign Optimizer") as demo:
    gr.Markdown("# 🚀 Multi-Agent Ad Campaign Optimizer")
    gr.Markdown("Paste your campaign JSON → click **Optimize** → get recommendations.")

    inp = gr.Code(
        label="Campaign JSON",
        value=json.dumps(DEFAULT_JSON, indent=2),
        language="json",
    )

    btn = gr.Button("Optimize", variant="primary")
    out = gr.Code(label="Result", language="json")

    btn.click(fn=optimize, inputs=inp, outputs=out)

demo.launch(server_name="0.0.0.0", server_port=7860)

