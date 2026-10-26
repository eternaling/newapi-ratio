import json
import re

def rewrite_expr(expr: str) -> str:
    if not isinstance(expr, str):
        return expr
    pat_pair = re.compile(r'cc\s*\*\s*([0-9.]+)\s*\+\s*cc12h\s*\*\s*([0-9.]+)')
    def replace_pair(m):
        a = float(m.group(1))
        b = float(m.group(2))
        return f'cc * {a + b}'
    while pat_pair.search(expr):
        expr = pat_pair.sub(replace_pair, expr)
    # 兜底清理残留cc12h
    pat_single_cc12h = re.compile(r'\s*\+?\s*cc12h\s*\*\s*[0-9.]+\s*')
    expr = pat_single_cc12h.sub('', expr)
    expr = re.sub(r'\+\s*\+', '+', expr)
    expr = re.sub(r'\(\s*\+', '(', expr)
    expr = re.sub(r'\+\s*\)', ')', expr)
    expr = expr.strip()
    return expr

def main():
    try:
        with open("src.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[FATAL] Load src.json failed: {repr(e)}")
        raise

    error_models = []
    for model_name, val in list(data.items()):
        try:
            # 分支1：值直接是表达式字符串（你现在这批就是这种！！）
            if isinstance(val, str):
                data[model_name] = rewrite_expr(val)
            # 分支2：值是dict，里面带 tiered_expr
            elif isinstance(val, dict):
                if "tiered_expr" in val:
                    val["tiered_expr"] = rewrite_expr(val["tiered_expr"])
            else:
                print(f"[SKIP] {model_name}: type={type(val)}")
        except Exception as e:
            error_models.append(model_name)
            print(f"[WARN] {model_name} rewrite skip: {repr(e)}")

    out_path = "ratio_config-newapi.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {out_path}")
    if error_models:
        print(f"[SUMMARY] Skipped: {error_models}")
    else:
        print("[SUMMARY] All done")

if __name__ == "__main__":
    main()
