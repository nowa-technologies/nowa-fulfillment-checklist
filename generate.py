#!/usr/bin/env python3
"""Generate index.html for the AIKO Smart Toy US Compliance Report.

Source of truth: data.json (exported from the consolidated Notion board
"[Resent to SBay] [All in one version] HQTS Compliance Report - AIKO - PML").
Re-run after editing data.json:  python3 generate.py
"""
import json
import html
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
items = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))

# ---- ordering of type groups -------------------------------------------------
GROUPS = [
    ("1. Mandatory", "Mandatory", "Required by US law — must be done."),
    ("2. Contingent", "Contingent", "Required only if a condition applies (a state, a material, a test outcome)."),
    ("3. Voluntary", "Voluntary", "Not legally required — recommended / good practice."),
    ("4. Confirming (đang chốt)", "Confirming (đang chốt)", "Still being confirmed whether NOWA needs this."),
]

RISK_CLASS = {"High Risk": "bad", "Medium Risk": "mid", "Low Risk": "ok"}


def esc(s):
    return html.escape(s if s is not None else "")


def nl2br(s):
    return esc(s).replace("\n", "<br>")


def joinlist(v):
    if not v:
        return "—"
    return esc(", ".join(v))


def committed(it):
    return it.get("To-do") == "__YES__"


total = len(items)
n_committed = sum(1 for it in items if committed(it))
n_suggested = total - n_committed
by_type = {g[0]: sum(1 for it in items if it["Type"] == g[0]) for g in GROUPS}

# ---- category definitions (partner-facing) -----------------------------------
CATEGORY_DEFS = [
    ("Test report", "Laboratory test reports or certificates proving the product (or a specific component) meets a safety or chemical standard — normally issued by an accredited lab."),
    ("Labeling & Packaging", "Marks, labels, logos and warnings that must physically appear on the product or its packaging (e.g. country of origin, FCC logo, age range, safety warnings)."),
    ("Instructions", "Information to be provided in the user manual / instructions for use — operation, safety, maintenance, identifiers and similar."),
    ("Regulatory Affair", "Legal and regulatory obligations such as privacy rules, state registrations and chemical reporting — compliance with a law, rather than a physical test or label."),
]
by_cat = {c: sum(1 for it in items if it.get("Category") == c) for c, _ in CATEGORY_DEFS}
cats_html = "".join(
    f'<li><strong>{esc(c)}</strong> <span class="catnum">({by_cat.get(c, 0)})</span> — {esc(desc)}</li>'
    for c, desc in CATEGORY_DEFS
)

rows_html = []
for type_key, label, blurb in GROUPS:
    group_items = [it for it in items if it["Type"] == type_key]
    if not group_items:
        continue
    g_comm = sum(1 for it in group_items if committed(it))
    section = [f'''
    <h2>{esc(label)} <span class="count">{len(group_items)} items · {g_comm} committed</span></h2>
    <p class="blurb">{esc(blurb)}</p>
    <div class="tablewrap">
    <table>
      <thead><tr>
        <th style="width:34px">#</th>
        <th>Requirement</th>
        <th>Category</th>
        <th>Applies to</th>
        <th style="width:78px">Risk</th>
        <th style="width:70px">Lead&nbsp;time</th>
        <th style="width:96px">Status</th>
      </tr></thead>
      <tbody>''']
    for it in group_items:
        is_c = committed(it)
        row_cls = "committed" if is_c else "suggested"
        badge = ('<span class="tag ok">✅ Committed</span>' if is_c
                 else '<span class="tag mid">◻ HQTS-suggested</span>')
        risk = it.get("Risk Level") or ""
        risk_html = f'<span class="tag {RISK_CLASS.get(risk, "")}">{esc(risk)}</span>' if risk else "—"
        applies = joinlist(it.get("Applicable Items"))
        comp = joinlist(it.get("Applied Component"))
        lead = esc(it.get("Leadtime") or "—")
        what = it.get("WhatItIs")
        understand = it.get("To understand")
        # Law & Standards — muted citation line under the requirement (skip empty / N/A)
        law = it.get("Law & Standards")
        law_html = ""
        if law and law.strip().upper() != "N/A":
            law_html = f'<div class="law">§ {esc(law)}</div>'
        region = it.get("Regions")
        region_html = f'<div class="region">{esc(region)}</div>' if region else ""
        detail = []
        if what:
            detail.append(f'<div class="detail-block"><div class="dl">What it is</div>{nl2br(what)}</div>')
        if understand:
            detail.append(f'<div class="detail-block note"><div class="dl">To understand (ghi chú)</div>{nl2br(understand)}</div>')
        remark = it.get("Remark")
        if remark:
            detail.append(f'<div class="detail-block"><div class="dl">Remark</div>{nl2br(remark)}</div>')
        detail_html = ""
        if detail:
            detail_html = (f'<tr class="detailrow {row_cls}"><td></td><td colspan="6">'
                           + "".join(detail) + "</td></tr>")
        section.append(f'''
        <tr class="{row_cls}">
          <td class="id">{it["id"]}</td>
          <td><div class="req">{esc(it["Requirements"])}</div>{law_html}{badge}</td>
          <td>{esc(it.get("Category") or "—")}</td>
          <td><div>{applies}</div><div class="comp">Component: {comp}</div>{region_html}</td>
          <td>{risk_html}</td>
          <td>{lead}</td>
          <td><span class="tag bad-soft">{esc(it.get("Compliance Status") or "—")}</span></td>
        </tr>{detail_html}''')
    section.append("</tbody></table></div>")
    rows_html.append("".join(section))

today = date.today().isoformat()

PAGE = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIKO Smart Toy — US Market Compliance Report</title>
<style>
  :root{{ --bg:#f5f6f8; --card:#fff; --ink:#1b2330; --muted:#5b6573; --line:#e3e7ec; --accent:#3b5bdb;
    --ok-bg:#eaf6ec; --ok-ink:#1d6b2b; --bad-bg:#fdecea; --bad-ink:#9b2226; --warn-bg:#fff7e6; --warn-ink:#6a4e00;
    --committed:#f3f8f4; --suggested:#fbfbfc; }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;line-height:1.55;font-size:15px;}}
  .wrap{{max-width:1040px;margin:0 auto;padding:30px 20px 70px;}}
  header.doc{{border-bottom:3px solid var(--accent);padding-bottom:16px;margin-bottom:10px;}}
  .eyebrow{{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent);font-weight:700;}}
  h1{{font-size:25px;margin:6px 0;}}
  .meta{{color:var(--muted);font-size:13.5px;}}
  h2{{font-size:19px;margin:34px 0 4px;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;}}
  h2 .count{{font-size:12.5px;font-weight:600;color:var(--muted);}}
  .blurb{{color:var(--muted);font-size:13.5px;margin:0 0 8px;}}
  p{{margin:8px 0;}}
  .legend{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:16px 0;box-shadow:0 1px 2px rgba(20,30,50,.04);}}
  .legend ul{{margin:6px 0;padding-left:20px;}} .legend li{{margin:4px 0;font-size:14px;}}
  .purpose{{background:#eef2ff;border:1px solid #c7d2fe;border-left:4px solid var(--accent);border-radius:12px;padding:15px 20px;margin:18px 0;}}
  .purpose p{{margin:8px 0;font-size:14.5px;}}
  .focus{{background:var(--warn-bg);border-left:3px solid #f0d27a;border-radius:6px;padding:10px 14px;margin-top:12px;font-size:14px;}}
  .focus .dl{{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#6a4e00;font-weight:700;margin-bottom:4px;}}
  .cats ul{{margin:8px 0 2px;padding-left:20px;}} .cats li{{margin:6px 0;font-size:14px;}}
  .catnum{{color:var(--muted);font-weight:600;}}
  .stats{{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0;}}
  .stat{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 16px;min-width:108px;box-shadow:0 1px 2px rgba(20,30,50,.04);}}
  .stat .num{{font-size:22px;font-weight:800;}} .stat .lbl{{font-size:12px;color:var(--muted);}}
  .tablewrap{{overflow-x:auto;border:1px solid var(--line);border-radius:12px;background:var(--card);box-shadow:0 1px 2px rgba(20,30,50,.04);}}
  table{{width:100%;border-collapse:collapse;font-size:13.5px;min-width:720px;}}
  th,td{{text-align:left;padding:9px 11px;border-bottom:1px solid var(--line);vertical-align:top;}}
  th{{background:#eef1f4;font-weight:700;position:sticky;top:0;}}
  tr.committed td{{background:var(--committed);}}
  tr.suggested td{{background:var(--suggested);}}
  td.id{{color:var(--muted);font-variant-numeric:tabular-nums;}}
  .req{{font-weight:700;margin-bottom:3px;}}
  .law{{color:#46506a;font-size:11.5px;margin:2px 0 5px;font-style:italic;}}
  .comp{{color:var(--muted);font-size:12px;margin-top:3px;}}
  .region{{color:var(--muted);font-size:12px;margin-top:4px;}}
  .detailrow td{{font-size:13px;color:#2a3340;border-bottom:2px solid var(--line);}}
  .detail-block{{margin:4px 0 8px;}}
  .detail-block.note{{background:var(--warn-bg);border-left:3px solid #f0d27a;padding:8px 12px;border-radius:6px;}}
  .dl{{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:3px;}}
  .tag{{display:inline-block;font-size:11px;font-weight:700;padding:2px 9px;border-radius:20px;white-space:nowrap;}}
  .ok{{background:var(--ok-bg);color:var(--ok-ink);}} .bad{{background:var(--bad-bg);color:var(--bad-ink);}}
  .mid{{background:var(--warn-bg);color:var(--warn-ink);}}
  .bad-soft{{background:#f4f5f7;color:#6a727e;}}
  footer{{margin-top:40px;color:var(--muted);font-size:12.5px;border-top:1px solid var(--line);padding-top:14px;}}
</style>
</head>
<body>
<div class="wrap">
<header class="doc">
  <div class="eyebrow">NOWA · AIKO Smart Toy</div>
  <h1>US Market Compliance Report</h1>
  <div class="meta">Consolidated HQTS + Tina certification list · for SBay &amp; internal review · generated {today}</div>
</header>

<div class="purpose">
  <strong>Purpose of this document</strong>
  <p>This is a single, consolidated list of the US-market compliance requirements for the AIKO smart toy, merged from HQTS's compliance testing list and Tina's list. It is shared with SBay as one reference point so the requirements, their legal basis, risk level and lead time are clear in one place.</p>
  <p>The items marked <span class="tag ok">✅ Committed</span> are the ones NOWA currently intends to complete — but NOWA is also seeking SBay's further advice, because some of them may not be necessary in the current phase.</p>
  <div class="focus">
    <div class="dl">Issue to focus on</div>
    The full list is confirmed complete; what is not yet clear is the <strong>priority for this phase</strong>. We would like SBay to help review the committed items and advise <strong>which are genuinely required now</strong> (e.g. for the first US shipment and current sales channel) <strong>versus which can be deferred</strong> to a later phase — so NOWA can sequence testing and documentation correctly. Advice on whether any <span class="tag mid">◻ HQTS-suggested</span> items are needed at this stage is also welcome.
  </div>
</div>

<div class="legend">
  <strong>How to read this</strong>
  <ul>
    <li><span class="tag ok">✅ Committed</span> — NOWA intends to do this (checked "to-do" on the Notion board), pending SBay's advice on whether it is needed in the current phase. <span class="tag mid">◻ HQTS-suggested</span> — HQTS recommends but it is not committed.</li>
    <li><strong>Type</strong>: <em>Mandatory</em> (required by US law) · <em>Contingent</em> (required only if a condition applies) · <em>Voluntary</em> (recommended) · <em>Confirming</em> (still being decided).</li>
    <li><strong>Risk</strong>: <span class="tag bad">High Risk</span> <span class="tag mid">Medium Risk</span> <span class="tag ok">Low Risk</span>.</li>
    <li><strong>§</strong> under each requirement = the governing <em>Law &amp; Standard</em>; <strong>Region</strong> shows where it applies. The detail row (below each item) explains <em>what the requirement is</em>, plus bilingual notes where available.</li>
  </ul>
</div>

<div class="legend cats">
  <strong>Categories explained</strong>
  <ul>
    {cats_html}
  </ul>
</div>

<div class="stats">
  <div class="stat"><div class="num">{total}</div><div class="lbl">Total items</div></div>
  <div class="stat"><div class="num">{n_committed}</div><div class="lbl">✅ Committed</div></div>
  <div class="stat"><div class="num">{n_suggested}</div><div class="lbl">◻ HQTS-suggested</div></div>
  <div class="stat"><div class="num">{by_type["1. Mandatory"]}</div><div class="lbl">Mandatory</div></div>
  <div class="stat"><div class="num">{by_type["2. Contingent"]}</div><div class="lbl">Contingent</div></div>
  <div class="stat"><div class="num">{by_type["3. Voluntary"]}</div><div class="lbl">Voluntary</div></div>
  <div class="stat"><div class="num">{by_type["4. Confirming (đang chốt)"]}</div><div class="lbl">Confirming</div></div>
</div>

{"".join(rows_html)}

<footer>
  Source: consolidated Notion board "[Resent to SBay] [All in one version] HQTS Compliance Report — AIKO — PML",
  which merges Tina's list and the HQTS compliance testing list. Product: AIKO smart plush toy (US market).
  This page is a static snapshot generated from <code>data.json</code>; re-run <code>generate.py</code> after updating the data.
</footer>
</div>
</body>
</html>
'''

OUT = "sbay-sent-compliance-list.html"
(ROOT / OUT).write_text(PAGE, encoding="utf-8")
print(f"Wrote {OUT} — {total} items ({n_committed} committed / {n_suggested} suggested)")
for g in GROUPS:
    print(f"  {g[1]}: {by_type[g[0]]}")
