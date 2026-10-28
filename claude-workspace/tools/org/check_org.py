#!/usr/bin/env python3
"""Kiem so nhan su agent (org/agents.yaml + org/policy.yaml) va doi chieu cau hinh that.

Chi DOC, khong sua file nao.

    python check_org.py [--org <thu muc chua agents.yaml, policy.yaml>]

Mac dinh --org = ../../org tinh tu file script. Workspace (claude-workspace/) luon la
2 cap tren thu muc script, KHONG phu thuoc --org.

Moi loi in 1 dong `<MA> <id>: <mo ta>`. Co loi -> exit 1; sach -> in tom tat theo tang, exit 0.
"""
import argparse
import importlib.util
import os
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover - moi truong thieu PyYAML
    sys.exit("LOI: thieu PyYAML (pip install pyyaml)")

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_ORG = os.path.join(WS, "org")

REQUIRED = [
    "id", "chuc_danh", "tang", "bao_cao_cho", "loai", "model", "chi_phi", "ky_nang",
    "mang", "muc_du_lieu", "nguoi_duyet", "gate", "khi_het_han_muc", "trang_thai", "tu_ngay",
]
EXTRA_REQUIRED = {
    "cli-executor": ["cooldown_h"],
    "claude-subagent": ["tool"],
}
TANG_VALUES = (0, 1, 2, "tu-van")
LOAI_VALUES = ("claude-session", "claude-subagent", "cli-executor", "mcp-advisor")
CHI_PHI_VALUES = ("claude-quota", "free", "tra-phi")
MANG_VALUES = ("none", "web-search", "connector")
TRANG_THAI_VALUES = ("thu-viec", "chinh-thuc", "nghi")
GATE_VALUES = ("bat-buoc", "khong", "tuy-viec")
MISSING = object()


def load_yaml(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_frontmatter(path):
    """Tra dict frontmatter YAML cua file .md, hoac None neu khong co."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None
    text = text.lstrip("\ufeff")
    m = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def as_toolset(value):
    """Tap ten tool tu chuoi phay hoac list."""
    if value is None:
        return set()
    if isinstance(value, str):
        items = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        items = list(value)
    else:
        items = [value]
    return {str(x).strip() for x in items if str(x).strip()}


def load_delegate():
    path = os.path.join(WS, "tools", "delegate", "delegate.py")
    spec = importlib.util.spec_from_file_location("_stlab_delegate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(org_dir):
    errors = []

    def add(code, ident, msg):
        errors.append((code, ident, msg))

    try:
        doc = load_yaml(os.path.join(org_dir, "agents.yaml")) or {}
        policy = load_yaml(os.path.join(org_dir, "policy.yaml")) or {}
    except OSError as e:
        print(f"LOI doc so nhan su: {e}", file=sys.stderr)
        return 1

    agents = doc.get("agents") or []
    if not isinstance(agents, list):
        print("LOI: agents.yaml: 'agents' phai la danh sach", file=sys.stderr)
        return 1

    policy_data = policy.get("muc_du_lieu") or {}
    thu_tu = list(policy_data.get("thu_tu") or [])
    max_external = policy.get("nha_cung_cap_ngoai_toi_da")
    duong_cam = set(policy.get("duong_cam") or [])

    # --- id: trung + tap id hop le ---
    counts = {}
    for a in agents:
        ident = a.get("id")
        counts[ident] = counts.get(ident, 0) + 1
    for ident, n in counts.items():
        if n > 1:
            add("E-ID-TRUNG", ident, f"id '{ident}' xuat hien {n} lan")
    id_set = {i for i in counts if i is not None}

    tang_of = {}
    for a in agents:
        ident = a.get("id")
        if ident is not None and ident not in tang_of:
            tang_of[ident] = a.get("tang")

    for a in agents:
        ident = a.get("id", "?")
        loai = a.get("loai")

        # --- truong bat buoc ---
        for f in REQUIRED:
            if f not in a:
                add("E-THIEU-TRUONG", ident, f"thieu truong '{f}'")
        for f in EXTRA_REQUIRED.get(loai, []):
            if f not in a:
                add("E-THIEU-TRUONG", ident, f"thieu truong '{f}' (bat buoc cho {loai})")

        # --- enum ---
        if "tang" in a and a["tang"] not in TANG_VALUES:
            add("E-ENUM", ident, f"tang {a['tang']!r} khong thuoc {list(TANG_VALUES)}")
        if "loai" in a and a["loai"] not in LOAI_VALUES:
            add("E-ENUM", ident, f"loai {a['loai']!r} khong thuoc {list(LOAI_VALUES)}")
        if "chi_phi" in a and a["chi_phi"] not in CHI_PHI_VALUES:
            add("E-ENUM", ident, f"chi_phi {a['chi_phi']!r} khong thuoc {list(CHI_PHI_VALUES)}")
        if "mang" in a and a["mang"] not in MANG_VALUES:
            add("E-ENUM", ident, f"mang {a['mang']!r} khong thuoc {list(MANG_VALUES)}")
        if "muc_du_lieu" in a and a["muc_du_lieu"] not in thu_tu:
            add("E-ENUM", ident, f"muc_du_lieu {a['muc_du_lieu']!r} khong thuoc {thu_tu}")
        if "trang_thai" in a and a["trang_thai"] not in TRANG_THAI_VALUES:
            add("E-ENUM", ident, f"trang_thai {a['trang_thai']!r} khong thuoc {list(TRANG_THAI_VALUES)}")
        if "gate" in a and a["gate"] not in GATE_VALUES:
            add("E-ENUM", ident, f"gate {a['gate']!r} khong thuoc {list(GATE_VALUES)}")

        # --- bao cao cho ---
        bc = a.get("bao_cao_cho")
        if "bao_cao_cho" in a:
            if bc == "tuan":
                if a.get("tang") != 0:
                    add("E-BAO-CAO", ident, "chi tang 0 duoc bao cao cho 'tuan'")
            elif bc not in id_set:
                add("E-BAO-CAO", ident, f"bao_cao_cho {bc!r} khong co trong so")

        kh = a.get("khi_het_han_muc")
        if kh is not None and kh not in id_set:
            add("E-BAO-CAO", ident, f"khi_het_han_muc {kh!r} khong co trong so")

        # --- cap bac ---
        tang = a.get("tang")
        if bc in id_set and tang in TANG_VALUES:
            report_tang = tang_of.get(bc)
            if tang == "tu-van":
                if report_tang != 0:
                    add("E-CAP", ident, f"tu-van chi duoc bao cao cho tang 0 (dang bao cao tang {report_tang!r})")
            elif not (isinstance(report_tang, int) and not isinstance(report_tang, bool)
                      and report_tang < tang):
                add("E-CAP", ident, f"bao_cao_cho {bc!r} (tang {report_tang!r}) khong cap tren cua tang {tang!r}")

        # --- chi phi / tu duyet ---
        if a.get("chi_phi") == "tra-phi":
            add("E-TRA-PHI", ident, "chi_phi 'tra-phi' bi cam (chi tra Claude Pro)")
        if ident is not None and a.get("nguoi_duyet") == ident:
            add("E-TU-DUYET", ident, "nguoi_duyet trung chinh id (tu duyet viec cua minh)")

        # --- muc du lieu cua nha cung cap ngoai ---
        if a.get("chi_phi") == "free" and loai in ("cli-executor", "mcp-advisor"):
            mdl = a.get("muc_du_lieu")
            if mdl in thu_tu and max_external in thu_tu:
                if thu_tu.index(mdl) > thu_tu.index(max_external):
                    add("E-DU-LIEU", ident,
                        f"muc_du_lieu {mdl!r} cao hon nha_cung_cap_ngoai_toi_da {max_external!r}")

        # --- subagent: file .md phai khop ---
        if loai == "claude-subagent":
            path = os.path.join(WS, "custom", "agents", f"{ident}.md")
            if not os.path.isfile(path):
                add("E-SUBAGENT", ident, f"thieu file custom/agents/{ident}.md")
            else:
                fm = read_frontmatter(path)
                if fm is None:
                    add("E-SUBAGENT", ident, "file khong co frontmatter YAML hop le")
                else:
                    if fm.get("model") != a.get("model"):
                        add("E-SUBAGENT", ident,
                            f"frontmatter model {fm.get('model')!r} != model {a.get('model')!r}")
                    if as_toolset(fm.get("tools")) != as_toolset(a.get("tool")):
                        add("E-SUBAGENT", ident,
                            "tap tools trong frontmatter khac tap 'tool' trong agents.yaml")

    # --- doi chieu delegate.py ---
    try:
        dele = load_delegate()
        order = list(dele.ORDER)
        cooldown = dele.COOLDOWN_H
        forbidden = list(dele.FORBIDDEN)
    except (OSError, AttributeError, ImportError) as e:
        print(f"LOI nap tools/delegate/delegate.py: {e}", file=sys.stderr)
        return 1

    executors = {}
    for a in agents:
        if a.get("loai") == "cli-executor" and a.get("id") is not None:
            executors[a["id"]] = a
    official = {i for i, a in executors.items() if a.get("trang_thai") == "chinh-thuc"}
    if official != set(order):
        add("E-DELEGATE", "executor",
            f"tap cli-executor chinh-thuc {sorted(official)} != ORDER {order}")

    for ident, a in executors.items():
        status = a.get("trang_thai")
        if status in ("thu-viec", "chinh-thuc") and ident not in dele.ADAPTERS:
            add("E-DELEGATE", ident, "executor khong co trong ADAPTERS")
        if status != "nghi":
            want_cd = cooldown.get(ident)
            if a.get("cooldown_h") != want_cd:
                add("E-DELEGATE", ident, f"cooldown_h {a.get('cooldown_h')!r} != COOLDOWN_H {want_cd!r}")

    for i, ident in enumerate(order):
        a = executors.get(ident)
        if a is None:
            add("E-DELEGATE", ident, "executor trong ORDER khong co trong so")
            continue
        want_next = order[i + 1] if i + 1 < len(order) else None
        got = a.get("khi_het_han_muc", MISSING)
        seen = {ident}
        while got is not None and got != MISSING:
            if got in seen or got not in executors:
                add("E-DELEGATE", ident, f"chuoi khi_het_han_muc lap vong/id la tai {got!r}")
                got = MISSING
                break
            seen.add(got)
            nxt = executors[got]
            if nxt.get("trang_thai") == "chinh-thuc":
                break
            if nxt.get("trang_thai") in ("thu-viec", "nghi"):
                got = nxt.get("khi_het_han_muc", MISSING)
                continue
            add("E-DELEGATE", ident, f"trang_thai khong hop le tren chuoi tai {got!r}")
            got = MISSING
            break
        if got != want_next:
            add("E-DELEGATE", ident,
                f"khi_het_han_muc executor chinh-thuc dau tien {got!r} != {want_next!r} (executor thu {i + 1} trong ORDER)")

    # --- policy phai bao trum FORBIDDEN ---
    for pat in forbidden:
        if pat not in duong_cam:
            add("E-POLICY", pat, "thieu mau trong policy.duong_cam")

    # --- in ket qua ---
    for code, ident, msg in errors:
        print(f"{code} {ident}: {msg}")
    if errors:
        return 1

    by_tang = {}
    for a in agents:
        key = str(a.get("tang"))
        by_tang[key] = by_tang.get(key, 0) + 1
    parts = ", ".join(f"tang {k}: {by_tang.get(k, 0)}" for k in ("0", "1", "2", "tu-van"))
    print(f"OK: {len(agents)} agent ({parts})")
    return 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kiem so nhan su agent STLab (chi doc)")
    ap.add_argument("--org", default=DEFAULT_ORG,
                    help="thu muc chua agents.yaml va policy.yaml (mac dinh: ../../org)")
    args = ap.parse_args(argv)
    return check(os.path.abspath(args.org))


if __name__ == "__main__":
    sys.exit(main())
