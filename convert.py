import json
import re

def rewrite_expr(expr: str) -> str:
    """
    把  cc * x + cc12h * y 合并为 cc*(x+y)
    支持：cc * 0.125 + cc12h * 0.25
    支持：cc*0.125+cc12h*0.25（无空格）
    """
    # 捕获 cc12h * 数字
    pat = re.compile(r'cc\s*\*\s*([0-9.]+)\s*\+\s*cc12h\s*\*\s*([0-9.]+)')
    def sub_fn(m):
        a = float(m.group(1))
        b = float(m.group(2))
        return f'cc * {a + b}'
    out = pat.sub(sub_fn, expr)
    # 兜底：还有零散 cc12h 直接删除（防止原表达式写法不一样）
    out = re.sub(r'\s*\+?\s*cc12h\s*\*\s*[0-9.]+\s*', '', out)
    return out

def main():
    with open("src.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    for model_name, cfg in data.items():
        if "tiered_expr" in cfg:
            raw = cfg["tiered_expr"]
            cfg["tiered_expr"] = rewrite_expr(raw)
    out_path = "ratio_config-newapi.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"saved {out_path}")

if __name__ == "__main__":
    main()
