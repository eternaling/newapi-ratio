import json
import re

def rewrite_expr(expr: str) -> str:
    if not isinstance(expr, str):
        return expr

    cc12h_pat = re.compile(r'cc12h\s*\*\s*([0-9.]+)')
    total_add = 0.0
    for m in cc12h_pat.finditer(expr):
        try:
            val = float(m.group(1))
            total_add += val
        except Exception:
            pass

    s = cc12h_pat.sub("", expr)
    # 清理多余加号
    s = re.sub(r'\s*\+\s*$', '', s)
    s = re.sub(r'\+\s*\+', '+', s)
    s = re.sub(r'\(\s*\+', '(', s)
    s = re.sub(r'\+\s*\)', ')', s)
    s = re.sub(r'\s*\+\s*\+', '+', s)

    cc_pat = re.compile(r'cc\s*\*\s*([0-9.]+)')
    match_cc = cc_pat.search(s)
    if match_cc:
        try:
            old = float(match_cc.group(1))
            new_coeff = old + total_add
            s = cc_pat.sub(f'cc * {new_coeff}', s, count=1)
        except Exception:
            pass
    else:
        if total_add > 0:
            s = re.sub(r'tier\(', rf'tier("cc_auto", cc * {total_add} + ', s, count=1)
    return s.strip()


def main():
    try:
        with open("src.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[FATAL] Load src.json failed: {repr(e)}")
        raise

    error_models = []
    for model_name, cfg in list(data.items()):
        # ========== 关键修复：先判断是不是字典 ==========
        if not isinstance(cfg, dict):
            print(f"[SKIP] {model_name}: cfg is not dict, type={type(cfg)} value={cfg}")
            continue

        if "tiered_expr" in cfg:
            raw = cfg["tiered_expr"]
            try:
                cfg["tiered_expr"] = rewrite_expr(raw)
                if "cc12h" in cfg["tiered_expr"]:
                    print(f"[WARN] {model_name} still has cc12h after rewrite")
            except Exception as e:
                error_models.append(model_name)
                print(f"[WARN] {model_name} rewrite skip: {repr(e)}")

    out_path = "ratio_config-newapi.json"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] Saved {out_path}")
    except Exception as e:
        print(f"[FATAL] Write output failed: {repr(e)}")
        raise

    if error_models:
        print(f"[SUMMARY] Skipped models count: {len(error_models)} → {error_models}")
    else:
        print("[SUMMARY] All models processed successfully")


if __name__ == "__main__":
    main()
