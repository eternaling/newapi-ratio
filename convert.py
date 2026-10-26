import json
import re

def rewrite_expr(expr: str) -> str:
    if not isinstance(expr, str):
        return expr
    # 匹配任意位置 cc12h * 数字
    cc12h_pat = re.compile(r'cc12h\s*\*\s*([0-9.]+)')
    total_add = 0.0
    # 先提取所有cc12h系数
    for m in cc12h_pat.finditer(expr):
        val = float(m.group(1))
        total_add += val
    # 删除全部 cc12h * xxx 片段
    s = cc12h_pat.sub("", expr)
    # 清理残留多余 +、空格
    s = re.sub(r'\s*\+\s*$', '', s)
    s = re.sub(r'\+\s*\+', '+', s)
    s = re.sub(r'\(\s*\+', '(', s)
    s = re.sub(r'\+\s*\)', ')', s)

    # 把累加的系数合并进cc
    cc_pat = re.compile(r'cc\s*\*\s*([0-9.]+)')
    match_cc = cc_pat.search(s)
    if match_cc:
        old = float(match_cc.group(1))
        new_coeff = old + total_add
        s = cc_pat.sub(f'cc * {new_coeff}', s, count=1)
    else:
        # 极端情况：原表达式没有cc，但是有cc12h
        if total_add > 0:
            s = s.replace("tier(", f'tier("missing_cc", cc * {total_add} + ')
    return s.strip()


def main():
    try:
        with open("src.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed load src.json: {e}")
        raise

    error_models = []
    for model_name, cfg in data.items():
        if "tiered_expr" in cfg:
            raw = cfg["tiered_expr"]
            try:
                cfg["tiered_expr"] = rewrite_expr(raw)
            except Exception as e:
                error_models.append(model_name)
                print(f"WARN model {model_name} rewrite failed: {e}")

    out_path = "ratio_config-newapi.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Done. Output: {out_path}")
    if error_models:
        print(f"Warning: {len(error_models)} models rewrite skipped: {error_models}")

if __name__ == "__main__":
    main()
