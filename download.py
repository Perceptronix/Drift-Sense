import os

os.environ["HF_HUB_DISABLE_XET"] = "1"

from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="yogeshn07/SEMICON-2026-Localization-DS5-v1",
    repo_type="dataset",
    local_dir="SEMICON-2026-Localization-DS5-v1",
    max_workers=2,
    resume_download=True,
)0