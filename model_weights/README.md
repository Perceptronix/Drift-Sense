# DINOv2 Weights

`localization_inference.py` uses the DINOv2 ViT-S/14 backbone via `torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")`.

The pretrained weights are loaded automatically at runtime by the inference script.
