# Prompt Templates

Prompt templates that instruct an LLM to update **deprecated REST API code**
to the **latest specification**.

Every template shares the same task (fix deprecated code → latest spec).
They differ only in **what reference information is injected** and **how that
information is structured**. The filename encodes those two choices.

---

## Naming convention

A filename is `<index>_<code>.md`, where `<code>` is built from these letters:

| Letter | Meaning |
| :----: | ------- |
| `BL`    | **B**ase**L**ine — only a link to the latest spec is given |
| `D`    | **D**eprecated specification is provided |
| `L`    | **L**atest specification is provided |

And an optional suffix describes **how** that spec is supplied:

| Suffix | Meaning |
| :----: | ------- |
| *(none)* | Single combined document |
| `m`    | **M**erged — deprecated + latest combined into one source |
| `s`    | **S**plit — provided as two separate sources: natural language + code |
| `t`    | **T**ext only — natural language, no code |
| `c`    | **C**ode only — code snippets, no natural language |

> **Example:** `DsLs` = **D**eprecated **s**plit (NL + code) **+** **L**atest **s**plit (NL + code).

---

## Placeholders

Each template fills in these variables at runtime:

| Placeholder | Content |
| ----------- | ------- |
| `{user_query}` | The input code to be fixed |
| `{link}` | URL(s) to the latest API spec (baseline only) |
| `{deprecated}` / `{latest}` | Deprecated / latest spec as a single document |
| `{context}` | Deprecated + latest merged into one document |
| `{deprecated_natural_language}` / `{deprecated_code}` | Deprecated spec, split into NL / code |
| `{latest_natural_language}` / `{latest_code}` | Latest spec, split into NL / code |

---

## Templates

| # | File | Reference information provided |
| - | ---- | ------------------------------ |
| 0 | `0_BL.md`    | **Baseline.** Only a link to the latest spec — the model fetches and reasons from it |
| 1 | `1_D.md`     | Deprecated spec only |
| 2 | `2_L.md`     | Latest spec only |
| 3 | `3_DLm.md`   | Deprecated + latest **merged** into a single context |
| 4 | `4_DL.md`    | Deprecated + latest as **two separate** specs |
| 5 | `5_Ds.md`    | Deprecated **split** (NL + code) |
| 6 | `6_Ls.md`    | Latest **split** (NL + code) |
| 7 | `7_DLs.md`   | Deprecated (single) + latest **split** (NL + code) |
| 8 | `8_DsL.md`   | Deprecated **split** (NL + code) + latest (single) |
| 9 | `9_DsLs.md`  | Deprecated **split** + latest **split** (NL + code each) |
| 10 | `10_DcLc.md` | Deprecated + latest, **code only** |
| 11 | `11_DtLt.md` | Deprecated + latest, **text (NL) only** |

---

## Shared structure

Every template except the baseline (`0_BL.md`) follows the same skeleton:

1. **Instruction** — role + task framing
2. **Modification Procedure** — analyze deprecated → locate matching code → rewrite to latest
3. **Attention** — only touch deprecated parts, no refactoring, no comments
4. **Reference sections** — the spec(s), varying per template (see table above)
5. **Output Indicator** — output must be byte-identical to the input except for the fixed lines
