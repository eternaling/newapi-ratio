import json
import re

def rewrite_expr(expr: str) -> str:
    if not isinstance(expr, str):
        return expr

    # 精准匹配 cc * A + cc12h * B 这种相邻组合（basellm固定格式）
    pat_pair = re.compile(r'cc\s*\*\s*([0-9.]+)\s*\+\s*cc12h\s*\*\s*([0-9.]+)')
    def replace_pair(m):
        a = float(m.group(1))
        b = float(m.group(2))
        return f'cc * {a + b}'
    # 循环替换，直到没有匹配（一条表达式里面可能多组，两个tier分支就是两组）
    while pat_pair.search(expr):
        expr = pat_pair.sub(replace_pair, expr)

    # 兜底：如果出现 cc12h 单独存在（异常写法）直接删除
    pat_single_cc12h = re.compile(r'\s*\+?\s*cc12h\s*\*\s*[0-9.]+\s*')
    expr = pat_single_cc12h.sub('', expr)

    # 清理多余连续加号
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
    for model_name, cfg in list(data.items()):
        if not isinstance(cfg, dict):
            print(f"[SKIP] {model_name}: cfg is not dict, type={type(cfg)} value={cfg}")
            continue

        if "tiered_expr" in cfg:
            raw = cfg["tiered_expr"]
            try:
                new_expr = rewrite_expr(raw)
                cfg["tiered_expr"] = new_expr
                if "cc12h" in new_expr:
                    print(f"[WARN] {model_name} STILL contains cc12h! expr={new_expr}")
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
