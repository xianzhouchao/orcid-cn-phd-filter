# ORCID 数据清洗脚本

从 ORCID 原始数据中筛选出**中国青年博士**的完整职业记录，用于学术迁移研究。

## 筛选逻辑

1. **筛中国人**：任意一条记录 `Country=CN` 的 ORCID 全部保留
2. **筛博士**：`Title_Degree` 包含博士相关关键词（ph.d / doctorate / 博士 等）
3. **筛青年**：含博士记录的 `Start_Year >= PHD_YEAR_MIN`（默认 2000，可修改）

## 使用方法

### 第一步：安装依赖

确保已安装 Python（3.8 以上），然后在终端运行：

```bash
pip install pandas
```

### 第二步：修改脚本中的文件路径

用任意文本编辑器打开 `clean.py`，找到顶部这一行，改成你的 CSV 文件实际路径：

```python
INPUT_FILE = r"在这里填入你的 CSV 文件路径"   # ★ 修改这里
```

**Windows 示例：**
```python
INPUT_FILE = r"C:\Users\yourname\Desktop\test_raw_data.csv"
```

**Mac/Linux 示例：**
```python
INPUT_FILE = r"/Users/yourname/Downloads/test_raw_data.csv"
```

### 第三步：按需调整参数（可选）

同样在 `clean.py` 顶部，可以修改：

```python
PHD_YEAR_MIN = 2000    # 博士 Start_Year >= 此值才算"青年"，按需修改
```

### 第四步：运行

```bash
python clean.py
```

脚本会在 `output/` 文件夹下生成三个文件：

| 文件 | 内容 |
|------|------|
| `cn_phd_all_records.csv` | 符合条件的 ORCID 的**全部职业记录**（用于迁移分析） |
| `cn_phd_degree_rows.csv` | 仅博士那一行（用于核查关键词匹配是否准确） |
| `report.txt` | 清洗摘要报告（各步骤筛选数量） |

## 数据格式要求

输入 CSV 需包含以下列（列名大小写需完全一致）：

```
ORCID, Category, Title_Degree, Department, Organization,
Org_ID, Org_ID_Type, City, Region, Country,
Start_Year, Start_Month, End_Year, End_Month
```

## 博士关键词列表

默认匹配以下关键词（大小写不敏感）：

```
ph.d, phd, doctorate, doctoral, doctor of philosophy,
d.phil, dr., 博士, 博士研究生, doktor, doutorado,
doctorat, dottorato, doktorat
```

如需添加或删除关键词，修改 `clean.py` 中的 `PHD_KEYWORDS` 列表即可。
