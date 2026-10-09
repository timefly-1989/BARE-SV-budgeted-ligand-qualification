"""Check the published file hashes before running numerical replay."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
expected = json.loads((ROOT / "SHA256SUMS.json").read_text())
for name, digest in expected.items():
    p = ROOT / name
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        raise SystemExit("Archive mismatch: " + name)
print("PASS: " + str(len(expected)) + " archived file hashes")
