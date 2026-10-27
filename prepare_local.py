"""Download CPU models and verify synthesis using the repository SDK."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ["HF_HOME"] = str(ROOT / "models" / "hf-cache")
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

if __name__ == "__main__":
    # ONNX external-data validation requires actual neighboring model files.
    # Materialize only the links in this installation's downloaded snapshots.
    import shutil
    cache = ROOT / "models" / "hf-cache"
    for repo in (cache / "hub").glob("models--*"):
        for path in (repo / "snapshots").rglob("*"):
            if path.is_symlink():
                source = path.resolve(strict=True)
                if not source.is_relative_to(cache.resolve()):
                    raise RuntimeError(f"Unexpected cache link: {path}")
                temporary = path.with_name(path.name + ".materialized")
                shutil.copyfile(source, temporary)
                os.replace(temporary, path)
    from huggingface_hub import hf_hub_download
    from vieneu import Vieneu
    import numpy as np

    tts = Vieneu(mode="v3turbo", backend="onnx", device="cpu", precision="fp32", threads=4)
    hf_hub_download("pnnbao-ump/VieNeu-TTS-v3-Turbo", "speaker_encoder.onnx")
    voices = tts.list_preset_voices()
    print(f"Preset voices: {len(voices)}", flush=True)
    (ROOT / "outputs").mkdir(exist_ok=True)
    audio = tts.infer("Xin chào các bạn. Đây là giọng đọc thử nghiệm của VieNeu trên máy tính của tôi.", voice="Hải Đăng")
    assert np.isfinite(audio).all() and np.max(np.abs(audio)) > 0
    tts.save(audio, str(ROOT / "outputs" / "hello-vieneu.wav"))
    print(f"Generated {len(audio) / tts.sample_rate:.2f}s at {tts.sample_rate} Hz", flush=True)
