import streamlit as st
import folium
from streamlit_folium import st_folium
import networkx as nx
import pandas as pd

from data import get_graph_data, CLUSTER_COLORS
from algorithm import build_graph, get_mst, get_delivery_route, calculate_route_cost, get_mst_weight

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Origami Delivery Optimizer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
# Palette: Platinum #EEE2DF | Thistle #DEC1DB | Liberty #5B61B2
#          Bleu De France #2F80E4 | Little Boy Blue #6DA0E1
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
    --platinum:  #EEE2DF;
    --thistle:   #DEC1DB;
    --liberty:   #5B61B2;
    --bleu:      #2F80E4;
    --lbb:       #6DA0E1;
    --ink:       #1C1B2E;
    --ink-soft:  #4A4869;
    --surface:   #F8F5F4;
    --white:     #FFFFFF;
    --border:    #E4DCF0;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: var(--ink);
    background-color: var(--surface);
}

/* ── App background ── */
.stApp {
    background-color: var(--surface);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1.5px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--ink) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'DM Serif Display', serif !important;
    color: var(--liberty) !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: var(--platinum) !important;
    color: var(--liberty) !important;
    border: 1.5px solid var(--thistle) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--thistle) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 2px 8px rgba(91,97,178,0.07);
    overflow: visible;
    min-width: 0;
}
[data-testid="stMetricLabel"] {
    color: var(--ink-soft) !important;
    font-size: 0.62rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-family: 'DM Mono', monospace !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
    line-height: 1.3 !important;
}
[data-testid="stMetricValue"] {
    color: var(--liberty) !important;
    font-size: 1.3rem !important;
    font-weight: 700;
    font-family: 'DM Serif Display', serif !important;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: unset !important;
}
[data-testid="stMetricDelta"] { font-size: 0.72rem; }

/* ── Page header ── */
.page-header {
    background: linear-gradient(120deg, var(--liberty) 0%, var(--bleu) 100%);
    border-radius: 14px;
    padding: 22px 30px;
    margin-bottom: 20px;
    color: white;
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: -40px; right: -40px;
    width: 160px; height: 160px;
    background: rgba(255,255,255,0.06);
    border-radius: 50%;
}
.page-header h1 {
    margin: 0;
    font-family: 'DM Serif Display', serif;
    font-size: 1.6rem;
    font-weight: 400;
    color: white;
    letter-spacing: -0.01em;
}
.page-header p {
    margin: 6px 0 0;
    font-size: 0.82rem;
    opacity: 0.82;
    color: white;
    font-weight: 400;
    font-family: 'DM Sans', sans-serif;
}

/* ── Section label ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    color: var(--ink-soft);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin: 16px 0 7px;
    padding-bottom: 4px;
    border-bottom: 1px solid var(--border);
}

/* ── Compare table ── */
.compare-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    font-family: 'DM Sans', sans-serif;
}
.compare-table th {
    background: var(--platinum);
    color: var(--ink-soft);
    padding: 9px 13px;
    text-align: left;
    border-bottom: 2px solid var(--thistle);
    font-weight: 600;
    font-size: 0.75rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.compare-table td {
    padding: 9px 13px;
    border-bottom: 1px solid var(--platinum);
    color: var(--ink);
}
.compare-table tr:last-child td { border-bottom: none; }
.compare-table tr:hover td { background: #F5F0FB; }
.winner { color: var(--bleu); font-weight: 700; }

/* ── Info tip ── */
.info-tip {
    background: #EEF3FC;
    border-left: 3px solid var(--lbb);
    border-radius: 0 8px 8px 0;
    padding: 9px 13px;
    font-size: 0.78rem;
    color: var(--liberty);
    margin-top: 10px;
    line-height: 1.5;
}

/* ── Primary button ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(120deg, var(--liberty), var(--bleu)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 3px 12px rgba(47,128,228,0.3) !important;
    transition: box-shadow 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 5px 18px rgba(47,128,228,0.45) !important;
}

/* ── Headings in main area ── */
.stMarkdown h3 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: var(--liberty);
    letter-spacing: -0.01em;
    margin-bottom: 10px;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Checkbox ── */
.stCheckbox > label {
    font-size: 0.84rem !important;
    color: var(--ink) !important;
}

/* ── Selectbox / toggle labels ── */
.stSelectbox label, .stToggle label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--ink-soft) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] {
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--platinum) !important;
    color: var(--liberty) !important;
    border: 1.5px solid var(--thistle) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
nodes_pos, raw_edges, nodes_info = get_graph_data()
G = build_graph(raw_edges)

# Tách buildings và intersections
all_buildings  = sorted([n for n in nodes_pos if not n.startswith("Inters_")])
by_cluster     = {}
for n in all_buildings:
    c = nodes_info[n]["cluster"]
    by_cluster.setdefault(c, []).append(n)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>Origami Delivery Optimizer</h1>
  <p>Select buildings to deliver &nbsp;&middot;&nbsp; The system calculates the optimal route &nbsp;&middot;&nbsp; The Origami, Vinhomes Grand Park</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar: chọn tòa ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Select Buildings")

    # Quick-select
    col_a, col_b = st.columns(2)
    if col_a.button("Select All", use_container_width=True):
        for n in all_buildings:
            st.session_state[f"node_{n}"] = True
    if col_b.button("Clear All", use_container_width=True):
        for n in all_buildings:
            st.session_state[f"node_{n}"] = False

    selected_nodes = []
    CLUSTER_ORDER  = ["S6", "S7", "S8", "S9", "S10"]

    for cluster in CLUSTER_ORDER:
        color  = CLUSTER_COLORS.get(cluster, "#888")
        towers = by_cluster.get(cluster, [])
        st.markdown(
            f'<div class="section-label" style="color:{color};">&#9632; {cluster} &mdash; {len(towers)} buildings</div>',
            unsafe_allow_html=True
        )
        cols = st.columns(len(towers) if len(towers) <= 3 else 3)
        for idx, node in enumerate(towers):
            col = cols[idx % 3]
            label = node.replace(cluster + ".", "")
            checked = col.checkbox(
                label,
                key=f"node_{node}",
                value=st.session_state.get(f"node_{node}", False),
            )
            if checked:
                selected_nodes.append(node)

    st.divider()

    st.markdown('<div class="section-label">Settings</div>', unsafe_allow_html=True)
    start_node = st.selectbox(
        "Start point",
        ["Entrance_Main"] + selected_nodes,
        index=0,
    )
    show_all_edges = st.toggle("Show all graph edges", value=False)

    st.markdown("""
    <div class="info-tip">
    Check buildings above, choose a start point, then click <b>Calculate Optimal Route</b>.
    </div>
    """, unsafe_allow_html=True)

# ── Nút tính ──────────────────────────────────────────────────────────────────
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    compute = st.button(
        "Calculate Optimal Route",
        use_container_width=True,
        type="primary",
        disabled=len(selected_nodes) < 2,
    )

if len(selected_nodes) < 2:
    st.info("Select at least **2 buildings** from the sidebar to begin.")

# ── Compute ───────────────────────────────────────────────────────────────────
result = None
if compute and len(selected_nodes) >= 2:
    # Build a virtual subgraph: selected buildings + all intersections,
    # but connect every pair of selected buildings via their shortest path
    # in the full graph so the subgraph is always connected.
    relevant = set(selected_nodes) | {n for n in nodes_pos if n.startswith("Inters_")}
    relevant.add(start_node)
    subG = G.subgraph(relevant).copy()

    # If the subgraph is disconnected, add virtual edges between selected nodes
    # using full-graph shortest-path distances so MST stays scoped to our nodes.
    if not nx.is_connected(subG):
        targets = list(selected_nodes) + ([start_node] if start_node not in selected_nodes else [])
        for i, u in enumerate(targets):
            for v in targets[i+1:]:
                if not subG.has_edge(u, v):
                    try:
                        dist = nx.shortest_path_length(G, source=u, target=v, weight="weight")
                        subG.add_edge(u, v, weight=dist, virtual=True)
                    except nx.NetworkXNoPath:
                        pass

    work_graph = subG

    kruskal_mst = nx.minimum_spanning_tree(work_graph, algorithm="kruskal", weight="weight")
    prim_mst    = nx.minimum_spanning_tree(work_graph, algorithm="prim",    weight="weight")

    k_route = get_delivery_route(kruskal_mst, start_node=start_node)
    p_route = get_delivery_route(prim_mst,    start_node=start_node)

    k_cost = calculate_route_cost(G, k_route)
    p_cost = calculate_route_cost(G, p_route)

    result = {
        "kruskal": {"mst": kruskal_mst, "route": k_route, "cost": k_cost,
                    "mst_weight": get_mst_weight(kruskal_mst)},
        "prim":    {"mst": prim_mst,    "route": p_route,  "cost": p_cost,
                    "mst_weight": get_mst_weight(prim_mst)},
        "selected": selected_nodes,
        "start":    start_node,
        "best":     "kruskal" if k_cost <= p_cost else "prim",
    }
    st.session_state["result"] = result

# Giữ result giữa các lần rerun
if "result" in st.session_state and result is None:
    result = st.session_state["result"]

# ── Layout chính ──────────────────────────────────────────────────────────────
map_col, info_col = st.columns([3, 2])

with map_col:
    # Metrics
    if result:
        best   = result["best"]
        b_data = result[best]
        other  = "prim" if best == "kruskal" else "kruskal"
        o_data = result[other]

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Buildings", len(result["selected"]))
        mc2.metric("MST Weight", f"{b_data['mst_weight']:,} m")
        mc3.metric("Route Distance", f"{b_data['cost']:,} m",
                   delta=f"-{o_data['cost'] - b_data['cost']:,} m vs {other.title()}" if b_data['cost'] < o_data['cost'] else None)
        mc4.metric("Best Algorithm", best.title())
        st.markdown("")

    # Map
    center_lat = sum(v[0] for v in nodes_pos.values()) / len(nodes_pos)
    center_lon = sum(v[1] for v in nodes_pos.values()) / len(nodes_pos)

    fmap = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=17,
        tiles="CartoDB positron",
    )

    # Tất cả cạnh (mờ)
    if show_all_edges:
        for u, v, d in G.edges(data=True):
            folium.PolyLine(
                [nodes_pos[u], nodes_pos[v]],
                color="#BBBBBB", weight=1, opacity=0.4,
                tooltip=f"{u} ↔ {v}: {d['weight']} m"
            ).add_to(fmap)

    # MST + route nếu đã tính
    if result:
        best_data = result[result["best"]]

        # MST edges — Liberty blue, clean
        for u, v, d in best_data["mst"].edges(data=True):
            if u in nodes_pos and v in nodes_pos:
                folium.PolyLine(
                    [nodes_pos[u], nodes_pos[v]],
                    color="#6DA0E1", weight=2.5, opacity=0.75,
                    tooltip=f"MST: {u} — {v} ({d['weight']} m)"
                ).add_to(fmap)

        # Route — Liberty deep, thicker
        route = best_data["route"]
        route_coords = [nodes_pos[n] for n in route if n in nodes_pos]
        if len(route_coords) > 1:
            folium.PolyLine(
                route_coords,
                color="#5B61B2", weight=4.5, opacity=1,
                tooltip="Delivery Route"
            ).add_to(fmap)
            # Step numbers
            for i in range(len(route) - 1):
                if route[i] in nodes_pos and route[i+1] in nodes_pos:
                    mid = (
                        (nodes_pos[route[i]][0] + nodes_pos[route[i+1]][0]) / 2,
                        (nodes_pos[route[i]][1] + nodes_pos[route[i+1]][1]) / 2,
                    )
                    folium.Marker(mid, icon=folium.DivIcon(
                        html=f'<div style="background:#5B61B2;color:#fff;border-radius:10px;'
                             f'padding:2px 6px;font-size:9px;font-weight:700;font-family:DM Sans,sans-serif;'
                             f'white-space:nowrap;box-shadow:0 1px 4px rgba(91,97,178,0.4);">{i+1}</div>',
                        icon_size=(24, 16), icon_anchor=(12, 8)
                    )).add_to(fmap)

    # Vẽ tất cả nodes
    for node, coord in nodes_pos.items():
        cluster   = nodes_info[node]["cluster"]
        color     = CLUSTER_COLORS.get(cluster, "#9CA3AF")
        is_inters = node.startswith("Inters_")
        is_start  = (node == start_node)

        if result:
            is_selected = node in result["selected"]
        else:
            is_selected = node in selected_nodes

        if is_inters:
            # Giao lộ: chấm nhỏ xám
            folium.CircleMarker(
                location=coord, radius=4,
                color="#9CA3AF", weight=1, fill=True,
                fill_color="#9CA3AF", fill_opacity=0.6,
                tooltip=node
            ).add_to(fmap)
        elif is_start:
            # Start: clean marker với viền Liberty
            folium.CircleMarker(
                location=coord, radius=12,
                color="#5B61B2", weight=3,
                fill=True, fill_color="#2F80E4", fill_opacity=1,
                tooltip=f"Start: {node}",
                popup=node
            ).add_to(fmap)
            folium.Marker(coord, icon=folium.DivIcon(
                html=f'<div style="font-size:8px;font-weight:700;color:#1C1B2E;font-family:DM Mono,monospace;'
                     f'text-shadow:0 0 3px #fff,-1px 0 #fff,0 1px #fff,1px 0 #fff,0 -1px #fff;'
                     f'white-space:nowrap;margin-top:14px;">START</div>',
                icon_size=(40, 14), icon_anchor=(20, 0)
            )).add_to(fmap)
        elif is_selected:
            # Được chọn: tròn lớn màu cluster, viền trắng
            folium.CircleMarker(
                location=coord, radius=10,
                color="#FFFFFF", weight=2.5,
                fill=True, fill_color=color, fill_opacity=1,
                tooltip=node,
                popup=folium.Popup(f"<b>{node}</b><br>Cluster: {cluster}", max_width=150)
            ).add_to(fmap)
            # Label
            folium.Marker(coord, icon=folium.DivIcon(
                html=f'<div style="font-size:9px;font-weight:700;color:#111;'
                     f'text-shadow:0 0 3px #fff,-1px 0 #fff,0 1px #fff,1px 0 #fff,0 -1px #fff;'
                     f'white-space:nowrap;">{node}</div>',
                icon_size=(60, 14), icon_anchor=(30, -6)
            )).add_to(fmap)
        else:
            # Không chọn: tròn nhỏ mờ
            folium.CircleMarker(
                location=coord, radius=6,
                color=color, weight=1.5,
                fill=True, fill_color=color, fill_opacity=0.3,
                tooltip=node
            ).add_to(fmap)

    st_folium(fmap, width=None, height=530, returned_objects=[])

    # ── Map Legend ────────────────────────────────────────────────────────────
    legend_items = []
    CLUSTER_ORDER_LEGEND = ["S6", "S7", "S8", "S9", "S10"]
    for cl in CLUSTER_ORDER_LEGEND:
        c = CLUSTER_COLORS.get(cl, "#888")
        legend_items.append(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
            f'<span style="width:12px;height:12px;border-radius:50%;background:{c};'
            f'border:2px solid #fff;box-shadow:0 0 0 1.5px {c};display:inline-block;flex-shrink:0;"></span>'
            f'<span style="font-size:0.75rem;font-weight:600;color:#4A4869;">{cl}</span>'
            f'</span>'
        )
    legend_items.append(
        '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
        '<span style="width:28px;height:3px;background:#6DA0E1;display:inline-block;border-radius:2px;"></span>'
        '<span style="font-size:0.75rem;color:#4A4869;">MST Edge</span>'
        '</span>'
    )
    legend_items.append(
        '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
        '<span style="width:28px;height:4px;background:#5B61B2;display:inline-block;border-radius:2px;"></span>'
        '<span style="font-size:0.75rem;color:#4A4869;">Delivery Route</span>'
        '</span>'
    )
    legend_items.append(
        '<span style="display:inline-flex;align-items:center;gap:5px;">'
        '<span style="width:14px;height:14px;border-radius:50%;background:#2F80E4;'
        'border:2.5px solid #5B61B2;display:inline-block;flex-shrink:0;"></span>'
        '<span style="font-size:0.75rem;color:#4A4869;">Start</span>'
        '</span>'
    )
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;'
        'background:#fff;border:1.5px solid #E4DCF0;border-radius:10px;'
        'padding:9px 14px;margin-top:6px;">'
        '<span style="font-family:DM Mono,monospace;font-size:0.62rem;font-weight:600;'
        'color:#9CA3AF;letter-spacing:0.08em;text-transform:uppercase;margin-right:10px;">Legend</span>'
        + "".join(legend_items) +
        '</div>',
        unsafe_allow_html=True
    )

with info_col:
    if not result:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9CA3AF;">
          <div style="font-family:'DM Serif Display',serif;font-size:2.5rem;color:#DEC1DB;letter-spacing:-0.02em;">Origami</div>
          <div style="font-size:0.95rem;font-weight:500;margin-top:16px;color:#4A4869;">
            No route calculated yet
          </div>
          <div style="font-size:0.82rem;margin-top:6px;color:#9CA3AF;">
            Select buildings from the sidebar and click <b>Calculate Optimal Route</b>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        best  = result["best"]
        other = "prim" if best == "kruskal" else "kruskal"

        # ── Algorithm comparison ──────────────────────────────────────────────
        st.markdown("### Algorithm Comparison")
        k = result["kruskal"]
        p = result["prim"]
        k_win_mst   = "+" if k["mst_weight"] <= p["mst_weight"] else ""
        p_win_mst   = "+" if p["mst_weight"] <= k["mst_weight"] else ""
        k_win_route = "+" if k["cost"] <= p["cost"] else ""
        p_win_route = "+" if p["cost"] <= k["cost"] else ""

        st.markdown(f"""
        <table class="compare-table">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Kruskal {k_win_mst if k_win_mst and k_win_route else ""}</th>
              <th>Prim {p_win_mst if p_win_mst and p_win_route else ""}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>MST Weight</td>
              <td class="{'winner' if k_win_mst else ''}">{k['mst_weight']:,} m {k_win_mst}</td>
              <td class="{'winner' if p_win_mst else ''}">{p['mst_weight']:,} m {p_win_mst}</td>
            </tr>
            <tr>
              <td>Route Distance</td>
              <td class="{'winner' if k_win_route else ''}">{k['cost']:,} m {k_win_route}</td>
              <td class="{'winner' if p_win_route else ''}">{p['cost']:,} m {p_win_route}</td>
            </tr>
            <tr>
              <td>Stops</td>
              <td>{len(k['route'])}</td>
              <td>{len(p['route'])}</td>
            </tr>
          </tbody>
        </table>
        """, unsafe_allow_html=True)

        st.markdown(
            f'<div style="margin-top:8px;font-size:0.8rem;color:#2F80E4;font-weight:600;">'
            f'Best algorithm for this delivery: <b>{best.title()}</b>'
            f' (saves {abs(k["cost"] - p["cost"]):,} m)</div>',
            unsafe_allow_html=True
        )

        st.divider()

        # ── Delivery order ────────────────────────────────────────────────────
        st.markdown(f"### Delivery Order &mdash; {best.title()}")
        best_route = result[best]["route"]
        cumulative = 0
        route_rows = []
        for i, node in enumerate(best_route):
            seg = 0
            if i > 0:
                try:
                    seg = nx.shortest_path_length(G, source=best_route[i-1], target=node, weight="weight")
                except Exception:
                    seg = 0
            cumulative += seg
            route_rows.append({"Stop": i+1, "Node": node,
                                "Cluster": nodes_info[node]["cluster"],
                                "Seg (m)": seg, "Total (m)": cumulative})

        df = pd.DataFrame(route_rows)

        def color_cluster(val):
            c = CLUSTER_COLORS.get(val, "#888")
            return f"background-color:{c}22; color:{c}; font-weight:700"

        styled = (df.style
                  .applymap(color_cluster, subset=["Cluster"])
                  .format({"Seg (m)": "{:,}", "Total (m)": "{:,}"})
                  .set_properties(**{"font-size": "0.78rem"}))

        st.dataframe(styled, use_container_width=True, height=320)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", csv, "delivery_route.csv", "text/csv",
                           use_container_width=True)