"""
network.html_builder
====================
Builds the self-contained D3.js HTML visualization from character data
returned by ClaudeAnalyzer.
"""

import json
import textwrap

from .config import NetworkConfig


class HTMLBuilder:
    """Builds the self-contained D3.js HTML visualization from character data."""

    def __init__(self, config: NetworkConfig = None):
        self.config = config or NetworkConfig()

    # ── Data enrichment ──────────────────────────────────────────────────────

    def _enrich_nodes(self, chars: list) -> None:
        cfg = self.config
        for c in chars:
            group = c.get("group", "other")
            c["color"]      = cfg.GROUP_COLORS.get(group, cfg.DEFAULT_NODE_COLOR)
            c["groupLabel"] = cfg.GROUP_LABELS.get(group, "Other")

    def _enrich_links(self, rels: list) -> None:
        cfg = self.config
        for r in rels:
            rel_type = r.get("type", "other")
            r["color"] = cfg.LINK_COLORS.get(rel_type, cfg.DEFAULT_LINK_COLOR)
            r["dash"]  = cfg.LINK_DASH.get(rel_type, "")

    # ── Summary block ─────────────────────────────────────────────────────────

    @staticmethod
    def _build_summary_html(summary: str) -> str:
        return "".join(
            f"<p>{textwrap.fill(s.strip(), width=9999)}</p>"
            for s in summary.replace("\\n", "\n").split("\n")
            if s.strip()
        )

    # ── Public interface ──────────────────────────────────────────────────────

    def build(self, data: dict) -> str:
        title   = data.get("book_title", "Unknown Title")
        author  = data.get("author", "")
        summary = data.get("book_summary", "")
        chars   = data.get("characters", [])
        rels    = data.get("relationships", [])

        self._enrich_nodes(chars)
        self._enrich_links(rels)

        nodes_json      = json.dumps(chars, ensure_ascii=False)
        links_json      = json.dumps(rels,  ensure_ascii=False)
        summary_paras   = self._build_summary_html(summary)
        group_colors_js = json.dumps(self.config.GROUP_COLORS)
        link_colors_js  = json.dumps(self.config.LINK_COLORS)

        return self._render_template(
            title=title,
            author=author,
            summary_paras=summary_paras,
            nodes_json=nodes_json,
            links_json=links_json,
            group_colors_json=group_colors_js,
            link_colors_json=link_colors_js,
        )

    @staticmethod
    def _render_template(
        title: str,
        author: str,
        summary_paras: str,
        nodes_json: str,
        links_json: str,
        group_colors_json: str,
        link_colors_json: str,
    ) -> str:
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Character Network</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

  :root {{
    --bg: #f8f4ee;
    --surface: #f0ebe2;
    --gold: #b8884a;
    --gold-l: #c09a60;
    --muted: #8a7a6a;
    --dim: #b8a898;
    --text: #4a3f35;
    --border: #ddd5c8;
  }}

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(14px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes shimmer {{
    0%   {{ background-position: -200% center; }}
    100% {{ background-position:  200% center; }}
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 0.55; }}
    50%       {{ opacity: 0.95; }}
  }}
  @keyframes flowDash {{
    to {{ stroke-dashoffset: -12; }}
  }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Lora', serif;
    height: 100vh;
    overflow: hidden;
  }}

  body::after {{
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 100;
  }}

  header {{
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 10;
    padding: 16px 32px 22px;
    background: linear-gradient(to bottom, rgba(248,244,238,0.98) 60%, transparent);
    display: flex;
    align-items: baseline;
    gap: 14px;
    animation: fadeUp 0.6s ease both;
  }}
  header::after {{
    content: '';
    position: absolute;
    bottom: 0; left: 32px; right: 32px;
    height: 1px;
    background: linear-gradient(to right, transparent, var(--gold), transparent);
  }}
  header h1 {{
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 700;
    letter-spacing: 0.05em;
    background: linear-gradient(90deg, var(--gold) 0%, #e8d090 35%, #c8a050 55%, var(--gold-l) 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 5s linear infinite;
  }}
  header span {{
    font-size: 14px;
    color: var(--muted);
    font-style: italic;
  }}

  #graph {{ width: 100vw; height: 100vh; }}

  .link {{
    fill: none;
    stroke-width: 1.5;
    opacity: 0.45;
    transition: opacity 0.2s, stroke-width 0.2s;
  }}
  .link.highlighted {{
    opacity: 1;
    stroke-width: 2.5;
    stroke-dasharray: 8, 4;
    animation: flowDash 0.8s linear infinite;
  }}
  .link.dimmed {{ opacity: 0.05; }}

  .node {{ cursor: pointer; }}
  .node circle {{ stroke-width: 2; transition: stroke-width 0.2s; }}
  .node:hover circle {{ stroke-width: 3.5; }}

  .node-label {{
    font-family: 'Playfair Display', serif;
    pointer-events: none;
    text-anchor: middle;
    fill: var(--text);
    opacity: 0.9;
  }}

  .link-label {{
    font-family: 'Lora', serif;
    font-size: 10px;
    font-style: italic;
    text-anchor: middle;
    pointer-events: none;
    opacity: 0;
  }}

  /* Character detail panel — left */
  #panel {{
    position: fixed;
    left: 0; top: 0; bottom: 0;
    width: 300px;
    background: linear-gradient(to right, rgba(248,244,238,0.97) 78%, transparent);
    padding: 68px 28px 36px 28px;
    display: flex;
    flex-direction: column;
    pointer-events: none;
    opacity: 0;
    transform: translateX(-20px);
    transition: opacity 0.35s ease, transform 0.35s ease;
    border-right: 1px solid transparent;
    overflow-y: auto;
    scrollbar-width: none;
  }}
  #panel::-webkit-scrollbar {{ display: none; }}
  #panel.visible {{
    opacity: 1;
    transform: translateX(0);
    pointer-events: all;
    border-right-color: var(--border);
  }}

  #panel-bar {{ width: 30px; height: 2px; border-radius: 2px; margin-bottom: 12px; }}
  #panel-name {{
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    margin-bottom: 4px;
    line-height: 1.2;
    color: var(--text);
  }}
  #panel-group {{
    font-size: 10px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 16px;
  }}
  #panel-desc {{
    font-size: 15px;
    line-height: 1.78;
    color: #7a6a5a;
    margin-bottom: 22px;
    padding-left: 12px;
    border-left: 1px solid var(--dim);
    font-style: italic;
  }}
  #panel-rels h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 9px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--dim);
    margin-bottom: 12px;
  }}
  .rel-item {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-bottom: 11px;
    padding: 6px 10px;
    border-left: 2px solid transparent;
    border-radius: 0 4px 4px 0;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s, transform 0.2s;
  }}
  .rel-item:hover {{
    border-left-color: var(--gold);
    background: rgba(192,154,96,0.1);
    transform: translateX(4px);
  }}
  .rel-name {{
    font-family: 'Playfair Display', serif;
    font-size: 17px;
    font-weight: 700;
  }}
  .rel-label {{
    font-size: 13px;
    color: var(--muted);
    font-style: italic;
  }}

  /* Book summary — right */
  #summary {{
    position: fixed;
    right: 0; top: 0; bottom: 0;
    width: 290px;
    background: linear-gradient(to left, rgba(248,244,238,0.97) 78%, transparent);
    padding: 68px 28px 36px 18px;
    border-left: 1px solid var(--border);
    overflow-y: auto;
    scrollbar-width: none;
    animation: fadeUp 0.7s ease 0.15s both;
  }}
  #summary::-webkit-scrollbar {{ display: none; }}
  #summary h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 5px;
  }}
  #summary .author {{
    font-size: 14px;
    color: var(--muted);
    font-style: italic;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--dim);
  }}
  #summary p {{
    font-size: 15px;
    line-height: 1.82;
    color: #7a6a5a;
    margin-bottom: 13px;
    font-style: italic;
  }}

  .sep {{ height: 1px; background: var(--dim); margin: 3px 0; opacity: 0.5; }}

  #hint {{
    position: fixed;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    font-size: 12px;
    font-style: italic;
    color: var(--muted);
    letter-spacing: 0.08em;
    white-space: nowrap;
    background: rgba(248,244,238,0.75);
    border: 1px solid rgba(184,168,152,0.5);
    border-radius: 20px;
    padding: 6px 18px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    pointer-events: none;
    animation: pulse 3s ease-in-out infinite;
  }}
</style>
</head>
<body>

<header>
  <h1>{title}</h1>
  <span>{author}</span>
</header>

<svg id="graph"></svg>

<div id="panel">
  <div id="panel-bar"></div>
  <div id="panel-name"></div>
  <div id="panel-group"></div>
  <div id="panel-desc"></div>
  <div id="panel-rels">
    <h3>Connections</h3>
    <div id="rel-list"></div>
  </div>
</div>

<div id="summary">
  <h2>Summary</h2>
  <div class="author">{author}</div>
  {summary_paras}
</div>

<div id="hint">Click a character · Drag to explore · Scroll to zoom</div>

<script>
const rawNodes = {nodes_json};
const rawLinks = {links_json};

const GROUP_COLORS = {group_colors_json};
const LINK_COLORS  = {link_colors_json};

// ── Build adjacency map ──
const adj = {{}};
rawNodes.forEach(n => adj[n.id] = []);
rawLinks.forEach(l => {{
  if (adj[l.source] !== undefined) adj[l.source].push({{ id: l.target, label: l.label, type: l.type }});
  if (adj[l.target] !== undefined) adj[l.target].push({{ id: l.source, label: l.label, type: l.type }});
}});
const byId = {{}};
rawNodes.forEach(n => byId[n.id] = n);

// ── SVG setup ──
const svg = d3.select("#graph");
let W = window.innerWidth, H = window.innerHeight;
svg.attr("width", W).attr("height", H);

const defs = svg.append("defs");

// Glow filter
const flt = defs.append("filter").attr("id", "glow")
  .attr("x", "-50%").attr("y", "-50%").attr("width", "200%").attr("height", "200%");
flt.append("feGaussianBlur").attr("in", "SourceGraphic").attr("stdDeviation", "4").attr("result", "blur");
const fm = flt.append("feMerge");
fm.append("feMergeNode").attr("in", "blur");
fm.append("feMergeNode").attr("in", "SourceGraphic");

// Per-link gradient defs
rawLinks.forEach((l, i) => {{
  l._gradId = `lg${{i}}`;
  const grad = defs.append("linearGradient")
    .attr("id", l._gradId)
    .attr("gradientUnits", "userSpaceOnUse");
  l._gradEl = grad;
  l._stopA  = grad.append("stop").attr("offset", "0%");
  l._stopB  = grad.append("stop").attr("offset", "100%");
}});

const g = svg.append("g");
svg.call(d3.zoom().scaleExtent([0.2, 4]).on("zoom", e => g.attr("transform", e.transform)));

// ── Force simulation ──
const sim = d3.forceSimulation(rawNodes)
  .force("link", d3.forceLink(rawLinks).id(d => d.id)
    .distance(d => {{
      const t = d.type;
      if (t === "love" || t === "family") return 90;
      if (t === "conflict" || t === "rivalry") return 180;
      return 140;
    }})
    .strength(0.45))
  .force("charge", d3.forceManyBody().strength(-700))
  .force("center", d3.forceCenter(W / 2, H / 2))
  .force("collision", d3.forceCollide(d => (d.size || 14) + 24));

// ── Links ──
const link = g.append("g").selectAll("line")
  .data(rawLinks).join("line")
  .attr("class", "link")
  .attr("stroke", d => `url(#${{d._gradId}})`)
  .attr("stroke-dasharray", d => d.dash || null);

const linkLabel = g.append("g").selectAll("text")
  .data(rawLinks).join("text")
  .attr("class", "link-label")
  .attr("fill", d => LINK_COLORS[d.type] || "var(--muted)")
  .text(d => d.label || "");

// ── Nodes ──
const node = g.append("g").selectAll(".node")
  .data(rawNodes).join("g")
  .attr("class", "node")
  .call(d3.drag()
    .on("start", (e, d) => {{ if (!e.active) sim.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
    .on("drag",  (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
    .on("end",   (e, d) => {{ if (!e.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }})
  )
  .on("click",      (e, d) => {{ e.stopPropagation(); showPanel(d); setHL(d); }})
  .on("mouseenter", (e, d) => {{
    d3.select(e.currentTarget).select(".node-main")
      .style("filter", `drop-shadow(0 0 8px ${{d.color || '#c4a45a'}})`);
    if (!selected) hoverHL(d, true);
  }})
  .on("mouseleave", (e, d) => {{
    d3.select(e.currentTarget).select(".node-main")
      .style("filter", null);
    if (!selected) hoverHL(d, false);
  }});

// Glow halo for large nodes
node.filter(d => (d.size || 14) >= 22)
  .append("circle")
  .attr("r", d => (d.size || 14) + 10)
  .attr("fill", d => d.color || "#c4a45a")
  .attr("opacity", 0.07)
  .style("filter", "url(#glow)");

node.append("circle")
  .attr("class", "node-main")
  .attr("r", d => d.size || 14)
  .attr("fill", d => (d.color || "#c4a45a") + "1e")
  .attr("stroke", d => d.color || "#c4a45a");

node.append("text")
  .attr("class", "node-label")
  .attr("dy", d => (d.size || 14) + 15)
  .text(d => d.name)
  .style("font-size", d => {{
    const s = d.size || 14;
    if (s >= 26) return "16px";
    if (s >= 18) return "14.5px";
    return "13px";
  }})
  .attr("fill", d => d.color || "#c4a45a");

// ── Tick ──
sim.on("tick", () => {{
  rawLinks.forEach(l => {{
    if (!l.source || !l.target) return;
    l._gradEl
      .attr("x1", l.source.x).attr("y1", l.source.y)
      .attr("x2", l.target.x).attr("y2", l.target.y);
    l._stopA.attr("stop-color", l.source.color || "#c4a45a");
    l._stopB.attr("stop-color", l.target.color || "#c4a45a");
  }});
  link
    .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
    .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
  linkLabel
    .attr("x", d => (d.source.x + d.target.x) / 2)
    .attr("y", d => (d.source.y + d.target.y) / 2 - 5);
  node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
}});

// ── Interactions ──
let selected = null;
const conn = (l, d) => l.source.id === d.id || l.target.id === d.id;

function hoverHL(d, on) {{
  link
    .classed("highlighted", l => on && conn(l, d))
    .classed("dimmed",      l => on && !conn(l, d))
    .style("filter",        l => on && conn(l, d)
      ? `drop-shadow(0 0 5px ${{LINK_COLORS[l.type] || '#c4a45a'}})`
      : null);
  linkLabel.attr("opacity", l => on && conn(l, d) ? 0.9 : 0);
}}

function setHL(d) {{
  selected = d;
  link
    .classed("highlighted", l => conn(l, d))
    .classed("dimmed",      l => !conn(l, d))
    .style("filter",        l => conn(l, d)
      ? `drop-shadow(0 0 5px ${{LINK_COLORS[l.type] || '#c4a45a'}})`
      : null);
  linkLabel.attr("opacity", l => conn(l, d) ? 0.9 : 0);
}}

function showPanel(d) {{
  const panel = document.getElementById("panel");
  document.getElementById("panel-bar").style.background = d.color || "#c4a45a";
  document.getElementById("panel-name").textContent = d.name;
  document.getElementById("panel-name").style.color = d.color || "#e8dcc8";
  document.getElementById("panel-group").textContent = d.groupLabel || d.group || "";
  document.getElementById("panel-desc").textContent = d.description || "";

  const list = document.getElementById("rel-list");
  list.innerHTML = "";
  (adj[d.id] || []).forEach(r => {{
    const nb = byId[r.id];
    if (!nb) return;
    const div = document.createElement("div");
    div.className = "rel-item";
    div.innerHTML = `
      <div class="rel-name" style="color:${{nb.color || '#c4a45a'}}">${{nb.name}}</div>
      <div class="rel-label">${{r.label}}</div>
    `;
    div.addEventListener("click", () => {{
      const nd = rawNodes.find(n => n.id === r.id);
      if (nd) {{ showPanel(nd); setHL(nd); }}
    }});
    list.appendChild(div);
  }});
  panel.classList.add("visible");
}}

svg.on("click", () => {{
  selected = null;
  document.getElementById("panel").classList.remove("visible");
  link.classed("highlighted", false).classed("dimmed", false)
      .style("filter", null);
  linkLabel.attr("opacity", 0);
}});

window.addEventListener("resize", () => {{
  W = window.innerWidth; H = window.innerHeight;
  svg.attr("width", W).attr("height", H);
  sim.force("center", d3.forceCenter(W / 2, H / 2)).alpha(0.1).restart();
}});
</script>
</body>
</html>"""
