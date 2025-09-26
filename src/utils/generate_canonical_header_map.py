import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HEADER_MAP_PATH = ROOT / "header_flat_csv" / "INGRES_header_map.json"
OUT_PATH = ROOT / "header_flat_csv" / "INGRES_header_canonical_map.json"


NON_ALNUM = re.compile(r"[^a-z0-9]+")
UNIT_RE = re.compile(r"\(([^)]+)\)")


def normalize_unit(u: str) -> str | None:
    if not u:
        return None
    u = u.strip().lower().replace(" ", "")
    # Normalize common variants
    if u in {"mm"}:
        return "mm"
    if u in {"%", "percent", "percentage"}:
        return "percent"
    if u in {"ha", "hectare", "hectares"}:
        return "ha"
    if u in {"ham", "ha.m", "ha-m", "ha_m"}:
        return "ha_m"
    # Fallback: keep alnum/underscore only
    return NON_ALNUM.sub("_", u).strip("_") or None


def slugify(text: str) -> str:
    text = text.lower()
    # Domain standardizations (deterministic, not synonyms)
    text = text.replace("ground water", "groundwater")
    text = text.replace("sewages", "sewage")  # singularize common pattern
    text = text.replace("flash flood", "flash_flood")  # preserve phrase
    text = text.replace("water conservation structure", "water_conservation_structures")
    text = text.replace("tanks and ponds", "tanks_ponds")
    text = text.replace(" and ", " _and_ ")  # avoid joining into one token
    # Remove unit parentheses content already extracted separately
    text = UNIT_RE.sub("", text)
    # Collapse separators
    text = text.replace("|", " ")
    text = NON_ALNUM.sub("_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def parse_value_to_parts(val: str):
    # Split by pipe into ordered parts, capturing units
    parts = [p.strip() for p in val.split("|")]
    units: list[str] = []
    cleaned_parts: list[str] = []
    for p in parts:
        # handle cases like "Conditions(ham)" (no space before paren)
        m = UNIT_RE.search(p)
        if m:
            u = normalize_unit(m.group(1))
            if u:
                units.append(u)
            p = UNIT_RE.sub("", p)
        cleaned_parts.append(p.strip())
    return cleaned_parts, units


def detect_dimension(last_part: str) -> tuple[str | None, str]:
    token = last_part.strip().lower()
    dim_map = {"c": "c", "nc": "nc", "pq": "pq", "total": "total"}
    if token in dim_map:
        return dim_map[token], ""
    return None, last_part


def canonical_name_from_value(val: str, key: str) -> str:
    parts, units = parse_value_to_parts(val)
    dimension: str | None = None
    if parts:
        dim, last = detect_dimension(parts[-1])
        if dim is not None:
            dimension = dim
            parts = parts[:-1]
        else:
            # keep original if not a dimension token
            parts[-1] = last

    # Build base name from remaining parts
    base = "_".join(slugify(p) for p in parts if p)
    base = re.sub(r"_+", "_", base).strip("_")

    # Append dimension if present
    if dimension:
        base = f"{base}_{dimension}"

    # Choose a unit if any was found (prefer the last occurrence)
    unit = units[-1] if units else None
    if unit:
        base = f"{base}_{unit}"

    # Handle duplicate-key disambiguators like ".1"
    if "." in key and key.split(".")[-1].isdigit():
        base = f"{base}_v{key.split('.')[-1]}"

    # Final cleanup
    base = re.sub(r"_+", "_", base).strip("_")
    return base


def main():
    if not HEADER_MAP_PATH.exists():
        raise FileNotFoundError(f"Header map not found: {HEADER_MAP_PATH}")

    data = json.loads(HEADER_MAP_PATH.read_text(encoding="utf-8"))

    canonical: dict[str, str] = {}
    used: set[str] = set()

    # Preserve basic identity columns as conventional snake_case
    identity_keys = {"Year", "S.No", "STATE", "DISTRICT"}
    for k, v in data.items():
        if k in identity_keys:
            name = slugify(k.replace(".", "_"))
        else:
            name = canonical_name_from_value(v, k)

        # ensure uniqueness deterministically
        base = name
        i = 1
        while name in used:
            i += 1
            name = f"{base}_{i}"
        used.add(name)
        canonical[k] = name

    OUT_PATH.write_text(json.dumps(canonical, indent=2), encoding="utf-8")
    print(f"Wrote canonical header map to: {OUT_PATH}")


if __name__ == "__main__":
    main()
