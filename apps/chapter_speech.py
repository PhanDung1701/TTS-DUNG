"""Chapter parsing and resumable jobs, independent of the model and Gradio."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import uuid
import zipfile

import soundfile as sf


HEADING = re.compile(
    r"^\s*(?:#{1,6}\s*)?(?:\*\*)?CHƯƠNG\s+(\d+)"
    r"(?:\s*[:.\-–—]\s*.*|\s+.*)?(?:\*\*)?\s*$", re.IGNORECASE
)


def parse_chapters(script):
    chapters = []
    title, lines = None, []
    numbers = set()
    for line in script.lstrip("\ufeff").splitlines():
        match = HEADING.fullmatch(line)
        if match:
            if title is None and any(s.strip() for s in lines):
                raise ValueError("Có nội dung trước CHƯƠNG đầu tiên. Hãy đưa vào một chương.")
            if title is not None:
                chapters.append((title, "\n".join(lines).strip()))
            number = int(match.group(1))
            if number in numbers:
                raise ValueError(f"Trùng số chương {number}.")
            numbers.add(number)
            title, lines = line.strip().lstrip("#").strip().strip("*"), []
        else:
            lines.append(line)
    if title is None:
        raise ValueError("Mỗi chương cần bắt đầu bằng dòng CHƯƠNG 1, CHƯƠNG 2…")
    chapters.append((title, "\n".join(lines).strip()))
    for title, body in chapters:
        if not body:
            raise ValueError(f"{title}: chưa có nội dung đọc.")
    return chapters


def output_root():
    return Path(os.environ.get("VIENEU_CHAPTER_OUTPUT_DIR", "outputs/chapters")).resolve()


def merge_audio(paths, destination):
    """Copy blocks instead of holding a whole book in RAM."""
    info = sf.info(paths[0])
    with sf.SoundFile(str(destination), "w", samplerate=info.samplerate,
                      channels=info.channels, subtype="PCM_16", format="WAV") as target:
        for path in paths:
            with sf.SoundFile(str(path)) as source:
                if (source.samplerate, source.channels) != (info.samplerate, info.channels):
                    raise ValueError("Các chương khác tần số lấy mẫu hoặc số kênh.")
                for block in source.blocks(blocksize=65536):
                    target.write(block)


def run_chapters(script, settings, state, synthesize, stop_requested, merge=False):
    """Yield (job state, status, audio paths, zip path, merged path).

    Only completed, validated WAVs enter the cache. A changed chapter or voice
    gets a new fingerprint, while other completed chapters remain reusable.
    """
    chapters = parse_chapters(script)
    root = output_root()
    state = state or {"job": uuid.uuid4().hex, "cache": {}}
    job = str(state.get("job", ""))
    if not re.fullmatch(r"[a-f0-9]{32}", job):
        raise ValueError("Mã công việc không hợp lệ.")
    directory = root / job
    directory.mkdir(parents=True, exist_ok=True)
    cache = state.setdefault("cache", {})
    paths, records = [], []
    stopped = False
    for index, (title, body) in enumerate(chapters, 1):
        if stop_requested():
            stopped = True
            break
        fingerprint = hashlib.sha256(json.dumps(
            [body, settings], ensure_ascii=False, sort_keys=True
        ).encode("utf-8")).hexdigest()
        cached = directory / f"{fingerprint}.wav"
        error = None
        prefix = f"Chương {index}/{len(chapters)} — {title}"
        if not (cache.get(fingerprint) and cached.is_file()):
            source_path, last_status = None, "Không sinh được audio."
            try:
                for audio, status in synthesize(body):
                    last_status = status
                    if audio is not None:
                        source_path = audio
                    yield state, f"{prefix}: {status}", list(paths), None, None
                    if stop_requested():
                        break
                if stop_requested():
                    stopped = True
                    break
                if source_path is None:
                    raise ValueError(last_status)
                if sf.info(source_path).frames <= 0:
                    raise ValueError("Audio rỗng.")
                shutil.copyfile(source_path, cached)
                cache[fingerprint] = True
            except Exception as exc:
                error = str(exc)
        filename = f"{index:02d}.wav"
        record = {"chapter": title, "file": filename, "error": error}
        records.append(record)
        if error is None:
            destination = directory / filename
            shutil.copyfile(cached, destination)
            paths.append(str(destination))
        # Persist progress even if the page disconnects or a later chapter fails.
        (directory / "progress.json").write_text(json.dumps(
            {"state": state, "chapters": records}, ensure_ascii=False, indent=2
        ), encoding="utf-8")
        yield state, f"{prefix}: {'Lỗi: ' + error if error else 'Đã lưu ✓'}", list(paths), None, None

    merged = None
    extra = ""
    if merge and len(paths) == len(chapters):
        try:
            merged = str(directory / "full.wav")
            merge_audio(paths, merged)
        except Exception as exc:
            merged, extra = None, f" Không ghép được: {exc}"
    archive = None
    if paths:
        archive = str(directory / "chapters.zip")
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as bundle:
            for path in paths + ([merged] if merged else []):
                bundle.write(path, Path(path).name)
            bundle.writestr("chapters.json", json.dumps(records, ensure_ascii=False, indent=2))
    failures = [f"{r['chapter']}: {r['error']}" for r in records if r["error"]]
    status = f"{'Đã dừng' if stopped else 'Hoàn tất'}: {len(paths)}/{len(chapters)} chương đã lưu."
    if failures:
        status += "\n" + "\n".join(failures)
    if stopped or failures:
        status += "\nBấm Tạo tất cả / Tiếp tục để chạy lại các chương chưa xong."
    yield state, status + extra, paths, archive, merged
