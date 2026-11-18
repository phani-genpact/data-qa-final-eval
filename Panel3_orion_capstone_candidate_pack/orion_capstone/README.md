# Panel 3 Capstone: Orion Retail, source to report

Read this file first. It tells you what is in this folder, what to do with each part, where each answer goes, and how to hand in.

All data in this pack is **fictional**. There is **no time limit**.

---

## 1. What you are doing

You are the QA engineer on Orion Retail's **Daily Regional Sales** pipeline. A source system release (R2) is coming that changes the order-line schema. You will:

1. **Prove the July load end to end**, from source to report, with an automated test suite.
2. **Keep that suite up to date** when schemas change (schema checks and a GitHub Actions workflow).
3. **Use GenAI to create the test pack for R2**, then review what it gives you.

The July load contains **defects on purpose**. Your tests are meant to find them. A test that fails because it found a real problem is a good result, not a mistake.

## 2. What you receive

| You receive | What it is |
| --- | --- |
| This pack (`orion_capstone/` folder) | The data, schemas, mappings, starter code, and templates |
| The question paper (`Panel3_Capstone_Question_Paper.docx`) | The questions, the marks, and boxes for your written answers. Given to you separately. |

You answer in **two places**: in the **code files in this folder**, and in the **question paper document**. Section 4 shows which is which.

---

## 3. Folder structure

```
orion_capstone/
├── README.md                      <- this file
├── requirements.txt               <- Python packages to install
├── pytest.ini                     <- pytest settings (do not change)
│
├── data/                          <- READ ONLY. Every layer, source to report
│   ├── source_order_lines.csv         source system extract, v1 schema (1,000 order lines)
│   ├── reject_order_lines.csv         lines rejected during cleaning, with a reason
│   ├── curated_order_lines.csv        cleaned lines (source minus rejects), with batch_id
│   ├── dim_customer.csv               customer dimension, SCD Type 2
│   ├── dim_product.csv                product dimension
│   ├── fact_sales.csv                 fact table, one row per order line
│   ├── agg_daily_region_sales.csv     aggregate: one row per date and region
│   ├── rpt_daily_region_sales.csv     report extract: Daily Regional Sales
│   ├── rpt_monthly_kpi.csv            report extract: Monthly KPI (orders, revenue, AOV)
│   └── source_order_lines_v2_sample.csv   50-line sample in the NEW R2 schema
│
├── schemas/                       <- READ ONLY. The source schema contracts
│   ├── source_order_lines.v1.json     current schema
│   └── source_order_lines.v2.json     R2 schema
│
├── mappings/                      <- READ ONLY. The requirements (source-to-target rules)
│   ├── mapping_v1.md                  REQ-01 to REQ-09
│   └── mapping_v2.md                  v2: shows what changed, adds REQ-10 and REQ-11
│
├── docs/
│   └── orion_handbook_extracts.md     READ ONLY. Handbook sections S1, S5, S6, S7, S8
│
├── tests/                         <- YOU EDIT. Starter test files with TODOs
│   ├── conftest.py                    fixtures (Section B1)
│   ├── test_01_counts_totals.py       levels 1 and 2 (Section B2)
│   ├── test_02_keys_hash.py           levels 3 and 4 (Section B3)
│   ├── test_03_dimensions_grain.py    dimension and key checks (Section B4)
│   ├── test_04_aggregates_kpi.py      aggregate and report checks (Section B5)
│   └── test_05_schema_drift.py        schema drift checks (Section D2)
│
├── .github/workflows/
│   └── ci.yml                     <- YOU EDIT. Starter workflow (Section D3)
│
└── submission/
    └── defect_log.md              <- YOU EDIT. Defect log template (Section F4)
```

**Read only** means do not change those files. If you change the data to make a test pass, you have hidden the defect and will lose marks.

---

## 4. Where each answer goes

| Section | Question | Where you answer | How it is marked |
| --- | --- | --- | --- |
| **A** Strategy | A1, A2, A3 | **Question paper** (boxes) | Read |
| **B** Build the suite | B1 to B6 | **`tests/` folder** (code) | We run your tests against the data |
| **C** PySpark | C1 to C4 | **Question paper** (write code in the boxes; it is read, not run) | Read |
| **D** Schema changes | D1, D4 | **Question paper** | Read |
| | D2 | **`tests/test_05_schema_drift.py`** (code) | We run it |
| | D3 | **`.github/workflows/ci.yml`** (YAML) | Read, and checked for valid YAML |
| **E** GenAI test cases | E1, E2, E3, E4 | **Question paper** | Read |
| **F** Investigation | F1, F2, F3 | **Question paper** | Read |
| | F4 | **`submission/defect_log.md`** and the paper | Read |
| **G** AI safely | G1, G2 | **Question paper** | Read |

If a question says "Hand in the file", the answer is the file in this folder, not text in the paper.

---

## 5. Set up and run

You need Python 3.10 or later.

```bash
cd orion_capstone
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest
```

Always run `pytest` from the `orion_capstone/` folder (the one that contains `pytest.ini`).

- **At the start**, every test fails with `NotImplementedError` or reports a missing fixture. That is normal. They are starters.
- **When you have finished**, some tests should pass and some should fail. The failures are your findings. Use `pytest -q` for a short view and `pytest -x` to stop at the first failure.
- To run one file: `pytest tests/test_01_counts_totals.py`.
- To run one test: `pytest tests/test_01_counts_totals.py::test_L1_source_to_curated_rows`.

PySpark is **not** needed to run anything. Section C is written, not executed.

---

## 6. Suggested order of work

1. **Read the use case and the rules** in the question paper (Instructions page).
2. **Read the requirements**: `mappings/mapping_v1.md`, then `mapping_v2.md`. Note how the layers connect: source → curated (and rejects) → fact → aggregate → reports. The grain of the fact table is one row per order line, identified by `order_id` and `line_no`.
3. **Look at the data** in pandas or a spreadsheet. Check the row counts and column names of each file.
4. **Section B**: complete `conftest.py` first (B1), then the test files in order.
5. **Section D2 and D3**: schema drift tests and the CI workflow.
6. **Run `pytest`** and read every failure message.
7. **Section F**: use your test results and pandas to complete the tie-out table, explain the differences, and write the defect report.
8. **Sections A, C, E, G**: written answers in the question paper. You can do these at any point. Section E needs the mapping files.
9. **Check the hand-in list** (Section 11) and zip the folder.

---

## 7. How to build the tests (Section B)

### 7.1 The pattern

Each test takes fixtures as arguments and asserts one thing. Give every assertion a message that shows the numbers, so a failure explains itself:

```python
def test_example(a, b):
    assert actual == expected, f"expected {expected}, got {actual}, difference {actual - expected}"
```

### 7.2 Conventions to follow

- **Fixtures (B1):** one per data file, in `conftest.py`, with `scope="session"` so each file loads once. Use the names in the TODO comment exactly, because the starter tests already use them. Parse `order_ts` as a datetime in `source` and `curated`.
- **Use the `KEY` constant** (`["order_id", "line_no"]`) from `conftest.py` instead of repeating the column names.
- **No hard-coded expected numbers.** Calculate expectations from the data. A test that says `assert len(fact) == 954` breaks as soon as the data changes.
- **No tolerance on counts.** Counts must match exactly. Only use a tolerance for money where rounding is documented.
- **Assertion messages** should show counts and a sample of the keys involved (for example the first five).
- **One test, one idea.** Tests should not depend on each other.
- **Round money to 2 decimals** when comparing sums.

### 7.3 Techniques you were taught

| Technique | Typical use |
| --- | --- |
| Count and sum | Row counts and control totals at each layer |
| Set difference or merge with `indicator=True` | Keys missing from, or extra in, a layer |
| Full outer join | Flag every row as missing, extra, or different |
| Row hash | Find silent value changes in rows whose keys match |
| Recompute from the layer below | Rebuild an aggregate or KPI yourself and compare |

### 7.4 Reading your results

- A test that **fails** should fail for a **real reason** shown in its message.
- A test that **passes** should pass because the data is right. Ask yourself: could this test ever fail? A check that compares a layer with the layer it was built from can pass even when both are wrong.
- Row counts matching does **not** prove a load is correct. Check totals, keys, and values too.
- A report that matches the layer under it can still be wrong. Prove numbers **from source**.

---

## 8. The data and requirements

### 8.1 How the layers connect

| Layer | File | Rule that applies |
| --- | --- | --- |
| Source | `source_order_lines.csv` | 1,000 order lines, one month (July 2026) |
| Rejects | `reject_order_lines.csv` | Lines with `qty <= 0` or `amount <= 0` (REQ-01) |
| Curated | `curated_order_lines.csv` | Source minus rejects. Cancelled lines stay here (REQ-02) |
| Fact | `fact_sales.csv` | Curated minus cancelled lines, plus `region` from the customer dimension |
| Aggregate | `agg_daily_region_sales.csv` | One row per `order_date` and `region` (REQ-06) |
| Reports | `rpt_*.csv` | Built from the aggregate (REQ-09) |

### 8.2 The requirements

The rules your tests should check are in `mappings/mapping_v1.md` (REQ-01 to REQ-09). Read each rule and decide which test proves it. `mapping_v2.md` shows the R2 changes and adds REQ-10 and REQ-11.

### 8.3 Schemas

The JSON files list every column of `source_order_lines` with its type and whether it can be NULL. Compare `v1` and `v2` to see the R2 change. The file `source_order_lines_v2_sample.csv` is what the new source looks like.

### 8.4 Handbook extracts

`docs/orion_handbook_extracts.md` has the handbook sections the questions refer to (the question paper prints the ones you need as H1 to H4). Use only what these extracts say when a question asks you to ground an answer in them.

---

## 9. How to write the answers in the question paper

- **Answer in the box** for the question. Keep to what is asked. If it says "one-line reason", write one line.
- **Use the numbers.** For Section F, work out the figures with your tests or pandas. Show money to 2 decimals.
- **Name things exactly:** requirement IDs (REQ-03), table names, test names, and column names.
- **Section A:** be concrete. Name the two layers you compare and what you compare, not just "check the counts".
- **Section C:** write PySpark (`F.col`, `.join`, `.groupBy`), not pandas. It will be read, not run. A small syntax slip is fine if the approach is right.
- **Section E:** use the six parts from session 1: Role, Context, Task, Format, Limits, Check. Make each part specific to the case. For E3, give each problem and its fix.
- **Section F:** show where each number comes from. For the defect report, use these fields: expected vs actual with the difference, sample keys, the query you used, likely root cause, and reports affected.
- **Section G:** an answer is grounded only if every claim is in the source. One unsupported claim means not grounded. Give a one-line reason.

---

## 10. AI and data rules

- **No AI tools** for any section except **Section E**. In Section E you may try your prompt in the approved AI tool.
- **Only the approved tool.** Never use a personal AI account.
- **Never paste real data** into any AI tool. Everything here is fictional, but build the habit: use invented or masked data only.
- **Never put secrets** (passwords, keys, tokens) in the repository, the workflow file, or a prompt. Credentials belong in GitHub Secrets.
- You may use the official documentation for Python, pandas, pytest, PySpark, and GitHub.

---

## 11. Hand-in checklist

Tick each item before you submit.

- [ ] `tests/conftest.py` has all nine fixtures
- [ ] `tests/test_01` to `test_04` are complete, with no `NotImplementedError` left
- [ ] `tests/test_05_schema_drift.py` has `diff_schemas`, the parametrized header test, and the breaking-change test
- [ ] `.github/workflows/ci.yml` has no TODO left and is valid YAML
- [ ] `submission/defect_log.md` is filled in
- [ ] You ran `pytest` and kept the output (you need it for Section F)
- [ ] The files in `data/`, `schemas/`, `mappings/` and `docs/` are **unchanged**
- [ ] The question paper has your written answers for A, C, D1, D4, E, F, and G
- [ ] You zipped the `orion_capstone/` folder (without `.venv`) and attached it to the question paper

**Hand in two things:** the zipped `orion_capstone` folder, and the completed question paper.

---

## 12. Troubleshooting

| Problem | Likely cause and fix |
| --- | --- |
| `fixture 'source' not found` | The fixture is not in `tests/conftest.py` yet, or its name differs from the one the test uses |
| `ModuleNotFoundError: conftest` | Run `pytest` from the `orion_capstone/` folder, not from inside `tests/` |
| `NotImplementedError` | The starter test is not completed yet |
| `FileNotFoundError` for a CSV | The path is wrong. Build it from `DATA` in `conftest.py`, which is based on the file location |
| Dates compare as text | Parse `order_ts` with `parse_dates=["order_ts"]`. `order_date` in fact and aggregate is text in `YYYY-MM-DD` form |
| Sums differ in the last decimal | Round both sides to 2 decimals before comparing |
| `.venv\Scripts\activate` is blocked on Windows | Run PowerShell as your user and allow scripts for the session, or use `cmd` instead |
| Workflow YAML will not parse | Check indentation (spaces, not tabs) and that `on:` is not left as `# TODO` only |

---

## 13. Marks

| Section | What it covers | Marks |
| --- | --- | --- |
| A | Plan the test strategy | 10 |
| B | Build the automated suite (Python, pandas, pytest) | 30 |
| C | PySpark reconciliation | 10 |
| D | Keep the suite current as schemas change | 14 |
| E | Test cases with GenAI | 16 |
| F | End-to-end investigation | 12 |
| G | Using AI answers safely | 8 |
| | **Total** | **100** |

Good luck.
