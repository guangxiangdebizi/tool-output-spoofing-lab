from __future__ import annotations

from pathlib import Path


OUT = Path("figures")


def svg_wrap(width: int, height: int, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M 0 0 L 10 5 L 0 10 z" fill="#243447"/>
    </marker>
    <style>
      .title {{ font: 700 22px Arial, sans-serif; fill: #17202a; }}
      .subtitle {{ font: 13px Arial, sans-serif; fill: #4f5b66; }}
      .label {{ font: 700 14px Arial, sans-serif; fill: #17202a; }}
      .small {{ font: 12px Arial, sans-serif; fill: #243447; }}
      .tiny {{ font: 10px Arial, sans-serif; fill: #243447; }}
      .box {{ stroke: #243447; stroke-width: 1.3; rx: 10; ry: 10; }}
      .green {{ fill: #dff5e3; }}
      .blue {{ fill: #dcecff; }}
      .yellow {{ fill: #fff0c9; }}
      .red {{ fill: #ffe0df; }}
      .purple {{ fill: #eadfff; }}
      .gray {{ fill: #f0f2f5; }}
      .hidden {{ stroke: #c0392b; stroke-width: 1.4; stroke-dasharray: 5 4; }}
      .arrow {{ stroke: #243447; stroke-width: 1.6; fill: none; marker-end: url(#arrow); }}
      .dashed {{ stroke-dasharray: 5 4; }}
    </style>
  </defs>
  <rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>
{body}
</svg>
"""


def rect(x: int, y: int, w: int, h: int, cls: str, title: str, lines: list[str]) -> str:
    text = [f'<text x="{x + 14}" y="{y + 24}" class="label">{title}</text>']
    for i, line in enumerate(lines):
        text.append(f'<text x="{x + 14}" y="{y + 46 + 17 * i}" class="small">{line}</text>')
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" class="box {cls}"/>\n' + "\n".join(text)


def arrow(x1: int, y1: int, x2: int, y2: int, dashed: bool = False) -> str:
    cls = "arrow dashed" if dashed else "arrow"
    return f'<path d="M {x1} {y1} L {x2} {y2}" class="{cls}"/>'


def figure10() -> str:
    body = [
        '<text x="40" y="36" class="title">End-to-end observation-spoofing overlay harness</text>',
        '<text x="40" y="58" class="subtitle">Only the model-visible observation plane changes; hidden truth and the original benchmark oracle stay fixed.</text>',
        rect(40, 90, 170, 95, "blue", "Official benchmark", ["task x", "tool/API environment", "original oracle O"]),
        rect(260, 90, 185, 95, "green", "Real execution", ["ground-truth tool plan", "stateful tool result y", "backend state s"]),
        rect(495, 70, 190, 115, "red", "Hidden/oracle plane", ["truth result y", "decisive fields", "oracle context", "not model-visible"]),
        rect(495, 235, 190, 115, "yellow", "Visible overlay", ["truthful y or spoofed y~", "schema-valid", "non-instructional"]),
        rect(735, 235, 190, 115, "purple", "Defense profile", ["schema / filter", "same-channel repeat", "read-back / authority"]),
        rect(970, 235, 175, 115, "gray", "Model decision", ["JSON final decision d", "claimed fields", "uncertainty / commit"]),
        rect(970, 70, 175, 115, "green", "Offline scoring", ["ASR / AFS / CU", "over-refusal", "cost + API errors"]),
        arrow(210, 137, 260, 137),
        arrow(445, 137, 495, 137),
        arrow(445, 137, 495, 292),
        arrow(685, 292, 735, 292),
        arrow(925, 292, 970, 292),
        arrow(1057, 235, 1057, 185),
        arrow(685, 127, 970, 127, dashed=True),
        '<text x="700" y="113" class="tiny">hidden truth used only by scorer</text>',
        '<path d="M 470 55 L 1170 55 L 1170 205 L 470 205 Z" fill="none" class="hidden"/>',
        '<text x="480" y="52" class="tiny" fill="#c0392b">oracle-only boundary</text>',
        '<path d="M 470 220 L 1170 220 L 1170 370 L 470 370 Z" fill="none" stroke="#1f618d" stroke-width="1.4" stroke-dasharray="5 4"/>',
        '<text x="480" y="217" class="tiny">model-visible boundary</text>',
    ]
    return svg_wrap(1200, 410, "\n".join(body))


def figure11() -> str:
    body = [
        '<text x="40" y="36" class="title">Scoring pipeline and restricted read-back projection boundary</text>',
        '<text x="40" y="58" class="subtitle">Projection scoring is allowed only for declared read-back paths; hidden oracle/raw results remain forbidden.</text>',
        rect(45, 95, 225, 125, "blue", "Primary truthful result y", ["canonical fields", "e.g. content/status/id", "exact-primary target"]),
        rect(45, 275, 225, 125, "red", "Forbidden sources", ["hidden oracle context", "raw tool result", "ground-truth plan", "never prompt-visible"]),
        rect(330, 95, 245, 125, "yellow", "Model claimed fields", ["claimed_fields[k]", "commit vs uncertainty", "action_commit flag"]),
        rect(655, 95, 260, 125, "green", "Exact-primary score", ["claim == truthful[k]", "strict object/field shape", "clean_utility_exact"]),
        rect(330, 285, 245, 135, "purple", "Read-back validator", ["split-channel observation", "content_verified=true", "visible validator_call"]),
        rect(655, 285, 260, 135, "green", "Restricted projection", ["whole object", "value/text/wifi_enabled", "records[*].declared keys", "clean_utility_semantic"]),
        rect(975, 185, 175, 125, "gray", "Reported metrics", ["ASR / AFS", "CU exact + semantic", "projection paths", "API/parse errors"]),
        arrow(270, 157, 330, 157),
        arrow(575, 157, 655, 157),
        arrow(575, 350, 655, 350),
        arrow(915, 157, 975, 220),
        arrow(915, 350, 975, 260),
        arrow(270, 337, 330, 337, dashed=True),
        '<path d="M 300 260 L 945 260" stroke="#c0392b" stroke-width="1.5" stroke-dasharray="6 5"/>',
        '<text x="340" y="252" class="tiny" fill="#c0392b">projection boundary: no arbitrary recursive matching, no oracle/raw access</text>',
        '<text x="47" y="440" class="small">Paper rule: projection can repair truthful read-back utility only; it must not change spoofed ASR.</text>',
    ]
    return svg_wrap(1200, 470, "\n".join(body))


def heat_cell(x: int, y: int, text: str, fill: str) -> str:
    return (
        f'<rect x="{x}" y="{y}" width="118" height="44" rx="7" ry="7" fill="{fill}" stroke="#d0d7de"/>'
        f'<text x="{x + 59}" y="{y + 27}" text-anchor="middle" class="tiny">{text}</text>'
    )


def figure12() -> str:
    cols = ["real exec", "full overlay", "leakage audit", "CI + paired", "multi-model", "autonomous"]
    rows = [
        ("AgentDojo", ["done", "1552 done", "done", "done", "missing", "no"]),
        ("ToolSandbox", ["done", "running", "pending", "pending", "missing", "no"]),
        ("Local surfaces", ["done", "pilot", "done", "pilot only", "missing", "no"]),
        ("Authorization", ["done", "pilot", "prompt ok", "pilot only", "missing", "no"]),
        ("tau/Web/SWE/RAG", ["design", "planned", "planned", "planned", "missing", "no"]),
    ]
    colors = {
        "done": "#dff5e3",
        "1552 done": "#dff5e3",
        "running": "#fff0c9",
        "pending": "#fff0c9",
        "pilot": "#e8f1ff",
        "pilot only": "#e8f1ff",
        "prompt ok": "#e8f1ff",
        "design": "#f0f2f5",
        "planned": "#f0f2f5",
        "missing": "#ffe0df",
        "no": "#ffe0df",
    }
    body = [
        '<text x="40" y="36" class="title">Experiment matrix completion heatmap</text>',
        '<text x="40" y="58" class="subtitle">Status snapshot for the first-model gpt-5.4-mini matrix; ToolSandbox full run was 6272/12384 cells at 2026-06-09 00:10 CST.</text>',
    ]
    x0, y0 = 175, 95
    for i, col in enumerate(cols):
        body.append(f'<text x="{x0 + i * 130 + 59}" y="84" text-anchor="middle" class="label">{col}</text>')
    for r, (name, vals) in enumerate(rows):
        y = y0 + r * 62
        body.append(f'<text x="45" y="{y + 27}" class="label">{name}</text>')
        for c, val in enumerate(vals):
            body.append(heat_cell(x0 + c * 130, y, val, colors[val]))
    body.extend(
        [
            '<rect x="45" y="415" width="18" height="18" fill="#dff5e3" stroke="#d0d7de"/><text x="72" y="429" class="small">completed full/canonical artifact</text>',
            '<rect x="300" y="415" width="18" height="18" fill="#fff0c9" stroke="#d0d7de"/><text x="327" y="429" class="small">running or pending after run completion</text>',
            '<rect x="600" y="415" width="18" height="18" fill="#e8f1ff" stroke="#d0d7de"/><text x="627" y="429" class="small">pilot / partial evidence</text>',
            '<rect x="830" y="415" width="18" height="18" fill="#ffe0df" stroke="#d0d7de"/><text x="857" y="429" class="small">missing for CCF-A full-paper claim</text>',
        ]
    )
    return svg_wrap(1000, 455, "\n".join(body))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "figure10_end_to_end_harness_dataflow.svg").write_text(figure10(), encoding="utf-8")
    (OUT / "figure11_scoring_projection_boundary.svg").write_text(figure11(), encoding="utf-8")
    (OUT / "figure12_experiment_completion_heatmap.svg").write_text(figure12(), encoding="utf-8")
    print("wrote camera-ready SVG figures")


if __name__ == "__main__":
    main()
