# Reflection

*Note: the handout text was not included in the repository, so these answers
address the four reflection prompts covered by the lab objectives.*

## 1. What is static code analysis and how does it differ from running the program?

Static analysis examines source code without executing it. It parses the code and
applies rules about style, API usage, data flow and known insecure patterns.
Running the program (dynamic testing) only exercises the paths you actually call
with the data you happen to supply. In this lab, `dairy_collection.py` ran and
printed sensible output, yet static analysis found a shell command built from
user input, an MD5 hash, an injectable SQL string, a global connection shadowed
by parameters, an unused import and several style defects. The three tools are
complementary: Pylint acts as a strict reviewer for logic/design, Flake8 enforces
PEP 8 grammar, and Bandit focuses on security patterns.

## 2. Which issues were the most serious and why?

Bandit's two High findings were the shell injection (`os.system` with a
concatenated `farmer` value, CWE-78) and the MD5 token (CWE-327). The shell issue
is the most dangerous because a farmer name containing shell metacharacters
could execute arbitrary commands with the program's privileges. The MD5 issue
weakens any security decision based on the token because MD5 collisions are
practical. The Medium SQL injection (CWE-89) could corrupt or read the ledger;
parameterized queries fixed it. Functional/style findings such as `fat == None`
and the ambiguous `l` are lower severity, but `fat == None` can produce silent
wrong results, so it was fixed as well.

## 3. How did severity affect the order of fixes, and what did re-running the tools show?

I fixed the High and Medium Bandit findings first, then the Flake8 style errors,
then the Pylint design/documentation issues, rerunning all three tools after each
group. The Pylint score rose from 2.00/10 to 3.21/10 after security and style
fixes, and finally to 10.00/10 after removing the global connection, adding
docstrings, renaming functions to snake_case and using an f-string. Bandit went
from 2 High + 1 Medium to zero issues, and Flake8 from 7 findings to zero.
Re-running was essential: reports are evidence, not just a to-do list, and they
confirm that a fix did not introduce a new problem.

## 4. How does static analysis improve quality and maintainability, and what are its limits?

It catches defects early, before code review or deployment, and makes standards
enforceable and repeatable instead of relying on memory. Renaming functions,
adding docstrings, removing the unused import and eliminating the global
connection made the ledger easier to read, test and extend; parameterized SQL
and the removal of shell execution made it safer. Its limits matter too: tools
produce false positives, they cannot prove business logic correct, and a clean
report does not replace tests, review or threat modelling. The best workflow is
to treat static analysis as a fast first pass, fix findings by severity, and use
the remaining effort on behavioural tests and design review.
