import json
import subprocess

raw = subprocess.check_output(
    [
        "python",
        "-m",
        "azure.cli",
        "cognitiveservices",
        "account",
        "list-models",
        "-g",
        "rg-ai-sales-poc",
        "-n",
        "oai-ms-poc",
        "-o",
        "json",
    ],
    text=True,
)
data = json.loads(raw)
for item in data:
    model = item.get("model") or item
    name = model.get("name") or item.get("name")
    version = model.get("version") or item.get("version")
    if not name:
        continue
    if any(k in name.lower() for k in ("gpt", "o4", "o3", "mini")):
        status = item.get("lifecycleStatus") or item.get("status") or ""
        print(f"{name}\t{version}\t{status}")
