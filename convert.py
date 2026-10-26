import json
import re

def rewrite_expr(expr: str) -> str:
    if not isinstance(expr, str):
        return expr

    # 匹配 cc * A + cc12h * B
    pat_pair_12h = re.compile(r'cc\s*\*\s*([0-9.]+)\s*\+\s*cc12h\s*\*\s*([0-9.]+)')
    def sub_12h(m):
        a = float(m.group(1))
        b = float(m.group(2))
        return f'cc * {a + b}'
    while pat_pair_12h.search(expr):
        expr = pat_pair_12h.sub(sub_12h, expr)

    # 匹配 cc * A + cc1h * B
    pat_pair_1h = re.compile(r'cc\s*\*\s*([0-9.]+)\s*\+\s*cc1h\s*\*\s*([0-9.]+)')
    def sub_1h(m):
        a = float(m.group(1))
        b = float(m.group(2))
        return f'cc * {a + b}'
    while pat_pair_1h.search(expr):
        expr = pat_pair_1h.sub(sub_1h, expr)

    # 兜底：清理任何残留 cc12h / cc1h 碎片（异常顺序写法）
    expr = re.sub(r'\s*\+?\s*cc12h\s*\*\s*[0-9.]+\s*', '', expr)
    expr = re.sub(r'\s*\+?\s*cc1h\s*\*\s*[0-9.]+\s*', '', expr)

    # 清理多余连续加号、括号旁边多余+
    expr = re.sub(r'\+\s*\+', '+', expr)
    expr = re.sub(r'\(\s*\+', '(', expr)
    expr = re.sub(r'\+\s*\)', ')', expr)
    expr = expr.strip()
    return expr


def main():
    with open("src.json", "r", encoding="utf-8") as f:
        root = json.load(f)

    # ✅ 关键：进入真正的 billing_expr 对象！！
    if not ("data" in root and "billing_expr" in root["data"]):
        raise Exception("json结构异常，找不到 data.billing_expr")

    billing_expr = root["data"]["billing_expr"]

    error_models = []
    for model_name, val in list(billing_expr.items()):
        try:
            if isinstance(val, str):
                billing_expr[model_name] = rewrite_expr(val)
        except Exception as e:
            error_models.append(model_name)
            print(f"[WARN] skip {model_name}: {repr(e)}")

    # 输出完整保留原始外层结构（data、billing_mode、success、message全部原样保留，只修改billing_expr内部字符串）
    out_path = "ratio_config-newapi.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2)

    # 校验输出
    with open(out_path, "r", encoding="utf-8") as fcheck:
        check_text = fcheck.read()
        has_cc12h = "cc12h" in check_text
        has_cc1h = "cc1h" in check_text
        print(f"[CHECK] cc12h存在：{has_cc12h}, cc1h存在：{has_cc1h}")

    print(f"[OK] write {out_path}")
    if error_models:
        print(f"[SKIPPED] count={len(error_models)} list={error_models}")


if __name__ == "__main__":
    main()
