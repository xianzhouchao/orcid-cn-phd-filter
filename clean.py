"""
clean.py - ORCID 数据清洗脚本

三步清洗：
  1. 筛选"中国人"：任意一条记录 Country=CN 的 ORCID
  2. 筛选"博士"：Title_Degree 包含博士相关关键词
  3. 筛选"青年"：含博士记录的 Start_Year >= PHD_YEAR_MIN

输出：
  output/cn_phd_all_records.csv    - 符合条件的 ORCID 的全部记录（用于迁移分析）
  output/cn_phd_degree_rows.csv    - 仅博士那一行（用于核查）
  output/report.txt                - 清洗摘要报告
"""

import os
import pandas as pd

# ============================================================
# ★ 可调参数
# ============================================================
INPUT_FILE   = r"在这里填入你的 CSV 文件路径"   # ★ 修改这里
OUTPUT_DIR   = os.path.join(os.path.dirname(__file__), "output")
CHUNK_SIZE   = 100_000          # 每次读取行数，内存不足可调小
PHD_YEAR_MIN = 2016             # ★ 博士 End_Year >= 此值才算"青年"（毕业年），按需修改

# 博士关键词（大小写不敏感模糊匹配）
PHD_KEYWORDS = [
    "ph.d", "phd", "doctorate", "doctoral", "doctor of philosophy",
    "d.phil", "dr.", "博士", "博士研究生", "doktor", "doutorado",
    "doctorat", "dottorato", "doktorat",
]
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 55)
print("ORCID 数据清洗")
print("=" * 55)

# ----------------------------------------------------------
# PASS 1：找出所有含 CN 记录的 ORCID
# ----------------------------------------------------------
print("\n[1/3] 扫描 Country=CN 的 ORCID...")
cn_orcids = set()
total_rows = 0

for chunk in pd.read_csv(INPUT_FILE, usecols=["ORCID", "Country"],
                         encoding="utf-8", chunksize=CHUNK_SIZE,
                         on_bad_lines="skip"):
    total_rows += len(chunk)
    cn_mask = chunk["Country"].astype(str).str.strip() == "CN"
    cn_orcids.update(chunk.loc[cn_mask, "ORCID"].dropna().unique())

print(f"  总行数: {total_rows:,}")
print(f"  含 CN 记录的 ORCID: {len(cn_orcids):,}")

# ----------------------------------------------------------
# PASS 2：在 CN 的 ORCID 中，找含博士记录且 Start_Year 符合的 ORCID
# ----------------------------------------------------------
print(f"\n[2/3] 筛选博士关键词（Start_Year >= {PHD_YEAR_MIN}）...")

# 构建正则，大小写不敏感
pattern = "|".join(PHD_KEYWORDS)

phd_orcids = set()
degree_rows = []   # 博士那一行，用于核查

for chunk in pd.read_csv(INPUT_FILE, usecols=["ORCID", "Title_Degree", "End_Year"],
                         encoding="utf-8", chunksize=CHUNK_SIZE,
                         on_bad_lines="skip"):
    # 只看 CN 的 ORCID
    chunk = chunk[chunk["ORCID"].isin(cn_orcids)]
    if chunk.empty:
        continue

    # 博士关键词匹配
    is_phd = chunk["Title_Degree"].astype(str).str.contains(pattern, case=False, na=False, regex=True)
    # 毕业年份筛选（End_Year >= PHD_YEAR_MIN）
    year_ok = pd.to_numeric(chunk["End_Year"], errors="coerce") >= PHD_YEAR_MIN

    matched = chunk[is_phd & year_ok]
    phd_orcids.update(matched["ORCID"].dropna().unique())
    degree_rows.append(matched)

print(f"  符合条件的 ORCID: {len(phd_orcids):,}")

# ----------------------------------------------------------
# PASS 3：导出符合条件 ORCID 的全部记录
# ----------------------------------------------------------
print("\n[3/3] 导出完整记录...")

all_records = []

for chunk in pd.read_csv(INPUT_FILE, encoding="utf-8",
                         chunksize=CHUNK_SIZE, on_bad_lines="skip"):
    matched = chunk[chunk["ORCID"].isin(phd_orcids)]
    if not matched.empty:
        all_records.append(matched)

df_all = pd.concat(all_records, ignore_index=True) if all_records else pd.DataFrame()
df_degree = pd.concat(degree_rows, ignore_index=True) if degree_rows else pd.DataFrame()

# 删除关键列有缺失的行
REQUIRED_COLS = ["ORCID", "Category", "Title_Degree", "Department",
                 "Organization", "City", "Country", "Start_Year"]
before = len(df_all)
df_all = df_all.dropna(subset=REQUIRED_COLS)
print(f"  删除缺失行: {before - len(df_all):,} 行，剩余 {len(df_all):,} 行")

out_all    = os.path.join(OUTPUT_DIR, "cn_phd_all_records.csv")
out_degree = os.path.join(OUTPUT_DIR, "cn_phd_degree_rows.csv")
out_report = os.path.join(OUTPUT_DIR, "report.txt")

df_all.to_csv(out_all, index=False, encoding="utf-8-sig")
df_degree.to_csv(out_degree, index=False, encoding="utf-8-sig")

# ----------------------------------------------------------
# 报告
# ----------------------------------------------------------
report = f"""ORCID 数据清洗报告
{'='*40}
输入文件      : {INPUT_FILE}
博士毕业年 >= : {PHD_YEAR_MIN}
必填列        : {REQUIRED_COLS}

原始总行数        : {total_rows:,}
含 CN 记录的 ORCID: {len(cn_orcids):,}
最终筛选 ORCID    : {len(phd_orcids):,}

输出文件：
  {out_all}
    行数（删缺失后）: {len(df_all):,}
  {out_degree}
    行数: {len(df_degree):,}
"""

with open(out_report, "w", encoding="utf-8") as f:
    f.write(report)

print(report)
print("完成！")
