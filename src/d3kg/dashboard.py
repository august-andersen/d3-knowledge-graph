"""Returns the full HTML string for the D3 force-directed knowledge graph visualization."""

import json


def generate_dashboard_html(graph_data: dict, show_labels: bool = False) -> str:
    data_json = json.dumps(graph_data)
    show_labels_js = "true" if show_labels else "false"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Knowledge Graph</title>
<style>
:root {{
  --bg: #0a0a0a;
  --text: #ffffff;
  --text-secondary: #999999;
  --edge: #333333;
  --edge-hover: #666666;
  --popup-bg: #1a1a1a;
  --popup-border: #333333;
  --input-bg: #1a1a1a;
  --input-border: #444444;
  --legend-bg: rgba(26, 26, 26, 0.9);
}}

[data-theme="light"] {{
  --bg: #fafafa;
  --text: #111111;
  --text-secondary: #666666;
  --edge: #cccccc;
  --edge-hover: #999999;
  --popup-bg: #ffffff;
  --popup-border: #dddddd;
  --input-bg: #ffffff;
  --input-border: #cccccc;
  --legend-bg: rgba(255, 255, 255, 0.95);
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  overflow: hidden;
  transition: background 0.3s, color 0.3s;
}}

svg {{
  width: 100vw;
  height: 100vh;
  display: block;
}}

#controls {{
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}}

#search {{
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  width: 300px;
  outline: none;
  transition: background 0.3s, border-color 0.3s, color 0.3s;
}}

#search::placeholder {{ color: var(--text-secondary); }}
#search:focus {{ border-color: #4ade80; }}

#theme-toggle {{
  position: fixed;
  top: 16px;
  right: 16px;
  z-index: 10;
  background: var(--input-bg);
  border: 1px solid var(--input-border);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 16px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.3s, border-color 0.3s, color 0.3s;
}}

#legend {{
  position: fixed;
  top: 16px;
  left: 16px;
  z-index: 10;
  background: var(--legend-bg);
  border: 1px solid var(--popup-border);
  border-radius: 8px;
  padding: 12px 16px;
  font-size: 12px;
  max-height: 300px;
  overflow-y: auto;
  transition: background 0.3s, border-color 0.3s;
}}

#legend h3 {{
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}}

.legend-item {{
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}}

.legend-dot {{
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}}

#stats {{
  position: fixed;
  bottom: 16px;
  left: 16px;
  z-index: 10;
  font-size: 12px;
  color: var(--text-secondary);
}}

#popup {{
  display: none;
  position: fixed;
  z-index: 20;
  background: var(--popup-bg);
  border: 1px solid var(--popup-border);
  border-radius: 12px;
  padding: 20px;
  max-width: 360px;
  min-width: 260px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  transition: background 0.3s, border-color 0.3s;
}}

#popup h2 {{
  font-size: 18px;
  margin-bottom: 4px;
}}

#popup .category-badge {{
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #fff;
}}

#popup .description {{
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 10px;
  line-height: 1.4;
}}

#popup .section-title {{
  font-size: 11px;
  text-transform: uppercase;
  color: var(--text-secondary);
  letter-spacing: 0.5px;
  margin: 10px 0 4px;
}}

#popup ul {{
  list-style: none;
  font-size: 13px;
}}

#popup ul li {{
  padding: 2px 0;
}}

#popup ul li .rel-label {{
  color: var(--text-secondary);
  font-size: 11px;
}}

#edge-tooltip {{
  display: none;
  position: fixed;
  z-index: 15;
  background: var(--popup-bg);
  border: 1px solid var(--popup-border);
  border-radius: 6px;
  padding: 6px 10px;
  font-size: 12px;
  pointer-events: none;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}
</style>
</head>
<body>

<div id="controls">
  <input type="text" id="search" placeholder="Search entities...">
</div>

<button id="theme-toggle">Light</button>

<div id="legend"><h3>Categories</h3></div>

<div id="stats"></div>

<div id="popup"></div>
<div id="edge-tooltip"></div>

<svg></svg>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const graphData = {data_json};
const showLabels = {show_labels_js};

const PALETTE = ['#4ade80','#60a5fa','#f472b6','#facc15','#a78bfa','#fb923c','#22d3ee','#e879f9','#34d399','#f87171','#818cf8','#fbbf24'];

// Build category color map
const categories = [...new Set(graphData.entities.map(e => e.category || 'unknown'))];
const categoryColor = {{}};
categories.forEach((cat, i) => {{
  categoryColor[cat] = PALETTE[i % PALETTE.length];
}});

// Build node connection counts
const connectionCount = {{}};
graphData.relationships.forEach(r => {{
  const s = r.source.toLowerCase();
  const t = r.target.toLowerCase();
  connectionCount[s] = (connectionCount[s] || 0) + 1;
  connectionCount[t] = (connectionCount[t] || 0) + 1;
}});

// Build nodes and links
const nodeMap = {{}};
const nodes = graphData.entities.map(e => {{
  const n = {{
    id: e.name,
    idLower: e.name.toLowerCase(),
    category: e.category || 'unknown',
    description: e.description || '',
    source_files: e.source_files || [],
    radius: Math.max(5, Math.min(20, 5 + (connectionCount[e.name.toLowerCase()] || 0) * 1.5))
  }};
  nodeMap[e.name.toLowerCase()] = n;
  return n;
}});

const links = graphData.relationships
  .filter(r => nodeMap[r.source.toLowerCase()] && nodeMap[r.target.toLowerCase()])
  .map(r => ({{
    source: nodeMap[r.source.toLowerCase()].id,
    target: nodeMap[r.target.toLowerCase()].id,
    label: r.label || 'relates to',
    weight: r.weight || 1
  }}));

// SVG setup
const svg = d3.select('svg');
const width = window.innerWidth;
const height = window.innerHeight;

const g = svg.append('g');

const zoom = d3.zoom()
  .scaleExtent([0.1, 8])
  .on('zoom', (event) => g.attr('transform', event.transform));
svg.call(zoom);

// Simulation
const simulation = d3.forceSimulation(nodes)
  .force('link', d3.forceLink(links).id(d => d.id).distance(d => 100 / d.weight))
  .force('charge', d3.forceManyBody().strength(-200))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(d => d.radius + 5));

// Links
const linkGroup = g.append('g').attr('class', 'links');
const link = linkGroup.selectAll('line')
  .data(links)
  .join('line')
  .attr('stroke', 'var(--edge)')
  .attr('stroke-width', d => d.weight)
  .attr('stroke-opacity', 0.6);

// Edge labels (if enabled)
let edgeLabel;
if (showLabels) {{
  edgeLabel = linkGroup.selectAll('text')
    .data(links)
    .join('text')
    .text(d => d.label)
    .attr('font-size', '9px')
    .attr('fill', 'var(--text-secondary)')
    .attr('text-anchor', 'middle')
    .attr('dy', -4);
}}

// Nodes
const nodeGroup = g.append('g').attr('class', 'nodes');
const node = nodeGroup.selectAll('circle')
  .data(nodes)
  .join('circle')
  .attr('r', d => d.radius)
  .attr('fill', d => categoryColor[d.category])
  .attr('stroke', 'var(--bg)')
  .attr('stroke-width', 1.5)
  .attr('cursor', 'grab')
  .call(d3.drag()
    .on('start', dragStart)
    .on('drag', dragging)
    .on('end', dragEnd));

// Node labels
const label = nodeGroup.selectAll('text')
  .data(nodes)
  .join('text')
  .text(d => d.id)
  .attr('font-size', d => Math.max(10, Math.min(14, d.radius + 2)) + 'px')
  .attr('fill', 'var(--text)')
  .attr('dx', d => d.radius + 4)
  .attr('dy', 4)
  .style('pointer-events', 'none')
  .style('opacity', nodes.length > 100 ? 0 : 1);

// Tick
simulation.on('tick', () => {{
  link
    .attr('x1', d => d.source.x)
    .attr('y1', d => d.source.y)
    .attr('x2', d => d.target.x)
    .attr('y2', d => d.target.y);

  if (showLabels && edgeLabel) {{
    edgeLabel
      .attr('x', d => (d.source.x + d.target.x) / 2)
      .attr('y', d => (d.source.y + d.target.y) / 2);
  }}

  node
    .attr('cx', d => d.x)
    .attr('cy', d => d.y);

  label
    .attr('x', d => d.x)
    .attr('y', d => d.y);
}});

// Drag
function dragStart(event, d) {{
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}}

function dragging(event, d) {{
  d.fx = event.x;
  d.fy = event.y;
}}

function dragEnd(event, d) {{
  if (!event.active) simulation.alphaTarget(0);
  // Pin node where it was dropped
  d.fx = event.x;
  d.fy = event.y;
}}

// Hover interactions
const connectedNodes = {{}};
links.forEach(l => {{
  const s = typeof l.source === 'object' ? l.source.id : l.source;
  const t = typeof l.target === 'object' ? l.target.id : l.target;
  if (!connectedNodes[s]) connectedNodes[s] = new Set();
  if (!connectedNodes[t]) connectedNodes[t] = new Set();
  connectedNodes[s].add(t);
  connectedNodes[t].add(s);
}});

node.on('mouseenter', function(event, d) {{
  const connected = connectedNodes[d.id] || new Set();
  node.attr('opacity', n => n.id === d.id || connected.has(n.id) ? 1 : 0.15);
  link.attr('opacity', l => {{
    const s = typeof l.source === 'object' ? l.source.id : l.source;
    const t = typeof l.target === 'object' ? l.target.id : l.target;
    return s === d.id || t === d.id ? 1 : 0.05;
  }});
  label.style('opacity', n => {{
    if (nodes.length > 100) return n.id === d.id || connected.has(n.id) ? 1 : 0;
    return n.id === d.id || connected.has(n.id) ? 1 : 0.15;
  }});
  if (showLabels && edgeLabel) {{
    edgeLabel.style('opacity', l => {{
      const s = typeof l.source === 'object' ? l.source.id : l.source;
      const t = typeof l.target === 'object' ? l.target.id : l.target;
      return s === d.id || t === d.id ? 1 : 0.05;
    }});
  }}
}});

node.on('mouseleave', function() {{
  node.attr('opacity', 1);
  link.attr('opacity', 0.6);
  label.style('opacity', nodes.length > 100 ? 0 : 1);
  if (showLabels && edgeLabel) edgeLabel.style('opacity', 1);
}});

// Edge hover tooltip
const edgeTooltip = d3.select('#edge-tooltip');
link.on('mouseenter', function(event, d) {{
  edgeTooltip
    .style('display', 'block')
    .style('left', (event.clientX + 10) + 'px')
    .style('top', (event.clientY - 20) + 'px')
    .html(`<strong>${{d.label}}</strong>`);
  d3.select(this).attr('stroke', 'var(--edge-hover)').attr('stroke-opacity', 1);
}});
link.on('mousemove', function(event) {{
  edgeTooltip
    .style('left', (event.clientX + 10) + 'px')
    .style('top', (event.clientY - 20) + 'px');
}});
link.on('mouseleave', function() {{
  edgeTooltip.style('display', 'none');
  d3.select(this).attr('stroke', 'var(--edge)').attr('stroke-opacity', 0.6);
}});

// Click popup
const popup = d3.select('#popup');

node.on('click', function(event, d) {{
  event.stopPropagation();
  const connected = connectedNodes[d.id] || new Set();
  const connections = links.filter(l => {{
    const s = typeof l.source === 'object' ? l.source.id : l.source;
    const t = typeof l.target === 'object' ? l.target.id : l.target;
    return s === d.id || t === d.id;
  }}).map(l => {{
    const s = typeof l.source === 'object' ? l.source.id : l.source;
    const t = typeof l.target === 'object' ? l.target.id : l.target;
    const other = s === d.id ? t : s;
    return `<li>${{other}} <span class="rel-label">${{l.label}}</span></li>`;
  }}).join('');

  const sourceFiles = d.source_files.length > 0
    ? d.source_files.map(f => `<li>${{f}}</li>`).join('')
    : '<li style="color:var(--text-secondary)">—</li>';

  popup.html(`
    <h2>${{d.id}}</h2>
    <span class="category-badge" style="background:${{categoryColor[d.category]}}">${{d.category}}</span>
    <div class="description">${{d.description}}</div>
    <div class="section-title">Source Files</div>
    <ul>${{sourceFiles}}</ul>
    <div class="section-title">Connections</div>
    <ul>${{connections || '<li style="color:var(--text-secondary)">None</li>'}}</ul>
  `);

  // Position near node
  let px = event.clientX + 20;
  let py = event.clientY - 40;
  if (px + 360 > window.innerWidth) px = event.clientX - 380;
  if (py + 300 > window.innerHeight) py = window.innerHeight - 320;
  if (py < 10) py = 10;

  popup
    .style('display', 'block')
    .style('left', px + 'px')
    .style('top', py + 'px');
}});

svg.on('click', () => popup.style('display', 'none'));
document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') popup.style('display', 'none');
}});

// Search
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', function() {{
  const q = this.value.toLowerCase().trim();
  if (!q) {{
    node.attr('opacity', 1);
    label.style('opacity', nodes.length > 100 ? 0 : 1);
    link.attr('opacity', 0.6);
    return;
  }}
  node.attr('opacity', d => d.idLower.includes(q) ? 1 : 0.1);
  label.style('opacity', d => d.idLower.includes(q) ? 1 : 0.05);
  link.attr('opacity', 0.05);
}});

// Legend
const legendEl = document.getElementById('legend');
categories.forEach(cat => {{
  const item = document.createElement('div');
  item.className = 'legend-item';
  item.innerHTML = `<span class="legend-dot" style="background:${{categoryColor[cat]}}"></span><span>${{cat}}</span>`;
  legendEl.appendChild(item);
}});

// Stats
const filesProcessed = new Set(graphData.entities.flatMap(e => e.source_files || [])).size;
document.getElementById('stats').textContent =
  `${{nodes.length}} entities, ${{links.length}} relationships, ${{filesProcessed}} files processed`;

// Theme
const themeBtn = document.getElementById('theme-toggle');
const savedTheme = localStorage.getItem('kg-theme') || 'dark';
if (savedTheme === 'light') {{
  document.body.setAttribute('data-theme', 'light');
  themeBtn.textContent = 'Dark';
}}

themeBtn.addEventListener('click', () => {{
  const isLight = document.body.getAttribute('data-theme') === 'light';
  if (isLight) {{
    document.body.removeAttribute('data-theme');
    themeBtn.textContent = 'Light';
    localStorage.setItem('kg-theme', 'dark');
  }} else {{
    document.body.setAttribute('data-theme', 'light');
    themeBtn.textContent = 'Dark';
    localStorage.setItem('kg-theme', 'light');
  }}
}});
</script>
</body>
</html>"""
