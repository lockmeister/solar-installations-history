#!/usr/bin/env python3
import csv, hashlib, json, os, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

DATASETS = {
    "SolarInstallationsByStreet.csv": "https://emidatasets.blob.core.windows.net/publicdata/Datasets/Retail/SolarInstallations/SolarInstallationsByStreet.csv",
    "SolarInstallationsByRegion.csv": "https://emidatasets.blob.core.windows.net/publicdata/Datasets/Retail/SolarInstallations/SolarInstallationsByRegion.csv",
}
EXPECTED_COLUMNS = {
    "SolarInstallationsByStreet.csv": ["StatisticalArea2Code", "StatisticalArea2Name", "PhysicalAddressStreet", "MarketSegment", "ICPs", "GenerationCapacityKilowattsAvg", "GenerationCapacityKilowattsSum"],
    "SolarInstallationsByRegion.csv": ["RegionType", "RegionCode", "Region", "MarketSegment", "ICPs", "GenerationCapacityKilowattsAvg", "GenerationCapacityKilowattsSum"],
}
ROOT = Path(__file__).resolve().parents[1]
CURRENT = ROOT / "data" / "current"
SNAPSHOTS = ROOT / "data" / "snapshots"
META = ROOT / "metadata" / "manifest.jsonl"


def fetch(name, url):
    req = Request(url, headers={"User-Agent": "lockmeister/solar-installations-history"})
    with urlopen(req, timeout=60) as r:
        data = r.read()
        headers = dict(r.headers.items())
    if not data.startswith((b"StatisticalArea2Code,", b"RegionType,")):
        raise RuntimeError(f"{name}: unexpected content start {data[:80]!r}")
    text = data.decode("utf-8-sig")
    reader = csv.reader(text.splitlines())
    cols = next(reader)
    expected = EXPECTED_COLUMNS[name]
    if cols != expected:
        raise RuntimeError(f"{name}: columns changed: {cols!r} != {expected!r}")
    row_count = sum(1 for _ in reader)
    return data, headers, row_count, cols


def main():
    today = os.environ.get("SNAPSHOT_DATE") or datetime.now(timezone.utc).date().isoformat()
    current_dir = CURRENT
    snapshot_dir = SNAPSHOTS / today
    current_dir.mkdir(parents=True, exist_ok=True)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    META.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for name, url in DATASETS.items():
        data, headers, row_count, cols = fetch(name, url)
        sha = hashlib.sha256(data).hexdigest()
        for dest in (current_dir / name, snapshot_dir / name):
            dest.write_bytes(data)
        records.append({
            "snapshot_date": today,
            "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "name": name,
            "url": url,
            "sha256": sha,
            "bytes": len(data),
            "rows": row_count,
            "columns": cols,
            "source_last_modified": headers.get("Last-Modified"),
            "source_etag": headers.get("ETag"),
        })
    existing = META.read_text() if META.exists() else ""
    with META.open("a", encoding="utf-8") as f:
        for rec in records:
            line = json.dumps(rec, sort_keys=True)
            if line not in existing:
                f.write(line + "\n")
    print(json.dumps(records, indent=2))

if __name__ == "__main__":
    main()
