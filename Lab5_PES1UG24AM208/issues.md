# Static Analysis Issues Found and Fixed

Tool versions: Pylint 4.1.4, Bandit 1.9.4, Flake8 7.5.0 (Python 3.14).

Baseline reports: `*_report_before.txt`. Final reports: `*_report_after.txt`
(also saved as `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt`).

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Bandit B605: `os.system("echo printing slip for " + farmer)` | Security (High, CWE-78) | 31 | User-controlled `farmer` was concatenated into a shell command, allowing command injection (e.g. `foo; rm -rf ...`). | Removed the shell entirely and the `os` import; the slip is now printed with `print()`. No shell interpretation is possible. |
| Bandit B324: `hashlib.md5(...)` for farmer tokens | Security (High, CWE-327) | 16 | MD5 is cryptographically broken (collisions) and unsuitable for identifiers/tokens. | Replaced with `hashlib.sha256(farmer.encode()).hexdigest()`. The demo token value changes, as expected for a stronger hash. |
| Bandit B608: SQL built with `.format()` | Security (Medium, CWE-89) | 11 | Farmer/day values were interpolated directly into an `INSERT` statement, enabling SQL injection and breaking on quotes. | Switched to a parameterized query with `?` placeholders and a value tuple; input is now bound by sqlite3, never parsed as SQL. |
| Pylint W0621: `conn` from outer scope redefined | Bug / design (Warning) | 6, 10, 19, 24, 34 | A module-level global connection was shadowed by parameters of the same name, hiding state and making import side effects. | Deleted the global `conn`; `main()` now creates the in-memory connection and passes it explicitly to every function. |
| Pylint C0114/C0116: missing module/function docstrings | Documentation (Convention) | 1, 10, 15, 19, 24, 30, 34, 39 | No docstrings, so purpose and contracts of the ledger functions were undocumented. | Added a module docstring and a one-line docstring to each of the seven functions. |
| Pylint C0103: camelCase function names | Style (Convention) | 10, 15, 19, 24, 30, 34 | `recordMilk`, `farmerToken`, `dailyTotal`, `topFarmer`, `printSlip`, `lowFat` violate PEP 8 snake_case. | Renamed to `record_milk`, `farmer_token`, `daily_total`, `top_farmer`, `print_slip`, `low_fat`, updating all call sites. |
| Pylint C0209 / Flake8 style: `%`-formatting and string concat | Style (Convention) | 21, 31, 33 | Old-style `%` formatting and string concatenation are harder to read and flagged by Pylint. | Used an f-string for the total (`f"Total: {total:.1f} litres"`) and kept a simple literal print for the slip. |
| Flake8 F401 / Pylint W0611: `import json` unused | Dead code (Warning) | 2 | Import brought in a module never referenced, adding noise and startup cost. | Removed the import. |
| Flake8 E501 / Pylint C0301: lines longer than 79/100 chars | Style (Convention) | 7, 11, 20, 25 | Long SQL and `CREATE TABLE` lines hurt readability and fail style checks. | Split each statement into a multi-line call / adjacent string literals, all under 79 characters. |
| Flake8 E741: ambiguous variable `l` | Style (Convention) | 26 | Single lowercase `l` is easily confused with `1` or `I`. | Renamed to `leader` (and lambda variable to `row`). |
| Flake8 E711 / Pylint C0121: `fat == None` | Bug (Convention) | 36 | Equality comparison with `None` can be wrong for objects with custom `__eq__`; PEP 8 requires `is`. | Changed to `fat is None`, preserving detection of missing fat readings. |
| Pylint (extra robustness): empty `rows` in `top_farmer` | Bug (pre-emptive) | 26 | `max()` on an empty ledger raised `ValueError` and crashed reporting for an empty day. | Added an early `if not rows: return None` guard; normal output is unchanged. |

## Verification

| Check | Before | After |
|-------|--------|-------|
| Pylint score | 2.00/10 | **10.00/10** |
| Bandit issues (High / Medium / Low) | 2 / 1 / 0 | **0 / 0 / 0** |
| Flake8 findings | 7 | **0** |
| Program output | Runs | Runs identically (except the stronger token hash) |

All three tools were rerun after each group of fixes; the final reports contain no
findings. The script still records two deliveries, prints the daily total, the top
farmer, low-fat farmers, a slip and a farmer token.
