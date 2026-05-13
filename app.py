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
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

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

.stApp { background-color: var(--surface); }

section[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1.5px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--ink) !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    font-family: 'DM Serif Display', serif !important;
    color: var(--liberty) !important;
    font-weight: 400 !important;
    letter-spacing: -0.01em;
}

section[data-testid="stSidebar"] .stButton > button {
    background: var(--platinum) !important;
    color: var(--liberty) !important;
    border: 1.5px solid var(--thistle) !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: var(--thistle) !important; }

[data-testid="stMetric"] {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 2px 8px rgba(91,97,178,0.07);
}
[data-testid="stMetricLabel"] {
    color: var(--ink-soft) !important;
    font-size: 0.62rem !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricValue"] {
    color: var(--liberty) !important;
    font-size: 1.3rem !important;
    font-weight: 700;
    font-family: 'DM Serif Display', serif !important;
}
[data-testid="stMetricDelta"] { font-size: 0.72rem; }

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
}
.page-header p {
    margin: 6px 0 0;
    font-size: 0.82rem;
    opacity: 0.82;
    color: white;
}

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

.stButton > button[kind="primary"] {
    background: linear-gradient(120deg, var(--liberty), var(--bleu)) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.2rem !important;
    box-shadow: 0 3px 12px rgba(47,128,228,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 5px 18px rgba(47,128,228,0.45) !important;
}

hr { border-color: var(--border) !important; }
.stCheckbox > label { font-size: 0.84rem !important; color: var(--ink) !important; }
.stSelectbox label, .stToggle label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--ink-soft) !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

[data-testid="stDataFrame"] {
    border: 1.5px solid var(--border) !important;
    border-radius: 10px !important;
}
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

# Force buildings to be dead-ends (Leaf Nodes)
for node in list(G.nodes()):
    if nodes_info[node]["cluster"] != "Road":
        edges = list(G.edges(node, data=True))
        if len(edges) > 1:
            best_edge = min(edges, key=lambda x: x[2]["weight"])
            for e in edges:
                if e[:2] != best_edge[:2] and e[:2] != (best_edge[1], best_edge[0]):
                    G.remove_edge(e[0], e[1])

def get_strict_dist(u, v):
    road_nodes = [n for n in G.nodes if nodes_info[n]["cluster"] == "Road"]
    safe_G = G.subgraph(road_nodes + [u, v]) 
    return nx.shortest_path_length(safe_G, source=u, target=v, weight="weight")

def get_strict_path(u, v):
    road_nodes = [n for n in G.nodes if nodes_info[n]["cluster"] == "Road"]
    safe_G = G.subgraph(road_nodes + [u, v])
    return nx.shortest_path(safe_G, source=u, target=v, weight="weight")

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

# ── Sidebar ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Select Buildings")

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
    
    START_OPTIONS = [
        "Entrance_Main", "Inters_pt_ad1", "Inters_ad2_ad3", 
        "Inters_ad3_ad5", "Inters_ad_ad5"
    ]
    
    start_node = st.selectbox("Start point", START_OPTIONS + selected_nodes, index=0)

    urgent_nodes = st.multiselect(
        "🚨 Urgent Deliveries (Priority):",
        options=selected_nodes,
        help="These nodes will be routed first before the rest."
    )
    
    show_all_edges = st.toggle("Show all graph edges", value=False)
    show_mst = st.toggle("Show MST lines", value=True)
    show_route = st.toggle("Show Delivery Route", value=True)

    st.divider()
    st.markdown('<div class="section-label">Compare Algorithms</div>', unsafe_allow_html=True)
    algo_choice = st.radio("Select Algorithm to display:", ["Kruskal", "Prim"], horizontal=True)

    st.markdown("""
    <div class="info-tip">
    Check buildings above, choose a start point, then click <b>Calculate Optimal Route</b>.
    </div>
    """, unsafe_allow_html=True)

# ── Compute Button ──────────────────────────────────────────────────────────────────
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

# ── Compute Logic ───────────────────────────────────────────────────────────────────
result = None
if compute and len(selected_nodes) >= 2:
    
    normal_nodes = [n for n in selected_nodes if n not in urgent_nodes]

    def solve_phase(start_pt, dest_nodes, algo_name):
        if not dest_nodes: 
            return [start_pt], 0, nx.Graph()
            
        targs = list(dest_nodes)
        if start_pt not in targs: 
            targs.insert(0, start_pt)
            
        wg = nx.Graph()
        for n in targs: wg.add_node(n)
        for i, u in enumerate(targs):
            for v in targs[i+1:]:
                try: 
                    wg.add_edge(u, v, weight=get_strict_dist(u, v))
                except Exception: 
                    pass
                    
        mst = nx.minimum_spanning_tree(wg, algorithm=algo_name, weight="weight")
        route = get_delivery_route(mst, start_node=start_pt, required_stops=targs)
        cost = sum(get_strict_dist(route[i], route[i+1]) for i in range(len(route)-1))
        return route, cost, mst

    def get_full_solution(algo_name):
        if not urgent_nodes:
            r, c, m = solve_phase(start_node, selected_nodes, algo_name)
            return {"u_route": [], "u_mst": nx.Graph(), "n_route": r, "n_mst": m, "f_route": r, "f_cost": c}
            
        u_route, u_cost, u_mst = solve_phase(start_node, urgent_nodes, algo_name)
        
        handoff_node = u_route[-1]
        n_route, n_cost, n_mst = solve_phase(handoff_node, normal_nodes, algo_name)
        
        f_route = u_route + n_route[1:] if len(n_route) > 1 else u_route
        f_cost = u_cost + n_cost
        
        return {
            "u_route": u_route, "u_mst": u_mst, 
            "n_route": n_route, "n_mst": n_mst, 
            "f_route": f_route, "f_cost": f_cost
        }

    result = {
        "kruskal": get_full_solution("kruskal"),
        "prim":    get_full_solution("prim"),
        "selected": selected_nodes
    }
    st.session_state["result"] = result

if "result" in st.session_state and result is None:
    result = st.session_state["result"]

# ── Main Layout ──────────────────────────────────────────────────────────────
map_col, info_col = st.columns([3, 2])

with map_col:
    if result:
        selected_key = "kruskal" if algo_choice == "Kruskal" else "prim"
        other_key    = "prim" if selected_key == "kruskal" else "kruskal"
        
        b_data = result[selected_key]
        o_data = result[other_key]
        
        # Calculate mathematical absolute best
        best_math_algo = "Kruskal" if result["kruskal"]["f_cost"] <= result["prim"]["f_cost"] else "Prim"

        active_mst_weight = (
            sum(d['weight'] for u, v, d in b_data["u_mst"].edges(data=True)) + 
            sum(d['weight'] for u, v, d in b_data["n_mst"].edges(data=True))
        )

        mc1, mc2, mc3, mc4 = st.columns(4)
        mc1.metric("Buildings", len(result["selected"]))
        mc2.metric("MST Weight", f"{active_mst_weight:,.1f} m")
        
        cost_diff = o_data['f_cost'] - b_data['f_cost']
        delta_str = f"{-cost_diff:,.1f} m vs {other_key.title()}" if cost_diff > 0 else None
        
        mc3.metric("Route Distance", f"{b_data['f_cost']:,.1f} m", delta=delta_str)
        mc4.metric("Best Algorithm", best_math_algo)
        st.markdown("")

    center_lat = sum(v[0] for v in nodes_pos.values()) / len(nodes_pos)
    center_lon = sum(v[1] for v in nodes_pos.values()) / len(nodes_pos)

    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=17, tiles="CartoDB positron")

    if show_all_edges:
        for u, v, d in G.edges(data=True):
            folium.PolyLine(
                [nodes_pos[u], nodes_pos[v]],
                color="#BBBBBB", weight=1, opacity=0.4,
                tooltip=f"{u} ↔ {v}: {d['weight']} m"
            ).add_to(fmap)

    if result:
        selected_key = "kruskal" if algo_choice == "Kruskal" else "prim"
        active_data = result[selected_key]

        if show_mst:
            def draw_mst(mst_graph, edge_color):
                for u, v, d in mst_graph.edges(data=True):
                    try:
                        path = get_strict_path(u, v)
                        path_coords = [nodes_pos[n] for n in path if n in nodes_pos]
                        folium.PolyLine(
                            path_coords, color=edge_color, weight=3, opacity=0.8,
                            dash_array="5, 8", tooltip=f"MST: {u} — {v} ({d['weight']:.1f} m)"
                        ).add_to(fmap)
                    except nx.NetworkXNoPath:
                        pass
            
            draw_mst(active_data["n_mst"], "#6DA0E1") 
            draw_mst(active_data["u_mst"], "#FF4B4B") 

        if show_route:
            def draw_route(route_list, line_color, start_step):
                for i in range(len(route_list) - 1):
                    try:
                        u, v = route_list[i], route_list[i+1]
                        path = get_strict_path(u, v)
                        path_coords = [nodes_pos[n] for n in path if n in nodes_pos]
                        
                        folium.PolyLine(
                            path_coords, color=line_color, weight=4.5, opacity=0.9,
                            tooltip=f"Step {start_step + i}: {u} ➔ {v}"
                        ).add_to(fmap)
                        
                        mid_coord = path_coords[len(path_coords) // 2]
                        folium.Marker(mid_coord, icon=folium.DivIcon(
                            html=f'<div style="background:{line_color};color:#fff;border-radius:10px;'
                                 f'padding:2px 6px;font-size:9px;font-weight:700;font-family:DM Sans,sans-serif;'
                                 f'white-space:nowrap;box-shadow:0 1px 4px rgba(0,0,0,0.4);">{start_step + i}</div>',
                            icon_size=(24, 16), icon_anchor=(12, 8)
                        )).add_to(fmap)
                    except nx.NetworkXNoPath:
                        pass
            
            draw_route(active_data["n_route"], "#5B61B2", start_step=len(active_data["u_route"]) if active_data["u_route"] else 1) 
            if active_data["u_route"]:
                draw_route(active_data["u_route"], "#E63946", start_step=1)

    for node, coord in nodes_pos.items():
        cluster   = nodes_info[node]["cluster"]
        color     = CLUSTER_COLORS.get(cluster, "#9CA3AF")
        is_inters = node.startswith("Inters_")
        is_start  = (node == start_node)
        is_selected = node in result["selected"] if result else node in selected_nodes

        if is_start:
            folium.CircleMarker(
                location=coord, radius=12, color="#5B61B2", weight=3,
                fill=True, fill_color="#2F80E4", fill_opacity=1, tooltip=f"Start: {node}", popup=node
            ).add_to(fmap)
            folium.Marker(coord, icon=folium.DivIcon(
                html=f'<div style="font-size:8px;font-weight:700;color:#1C1B2E;font-family:DM Mono,monospace;'
                     f'text-shadow:0 0 3px #fff,-1px 0 #fff,0 1px #fff,1px 0 #fff,0 -1px #fff;'
                     f'white-space:nowrap;margin-top:14px;">START</div>',
                icon_size=(40, 14), icon_anchor=(20, 0)
            )).add_to(fmap)
        elif is_inters:
            folium.CircleMarker(
                location=coord, radius=4, color="#9CA3AF", weight=1, fill=True,
                fill_color="#9CA3AF", fill_opacity=0.6, tooltip=node
            ).add_to(fmap)
        elif is_selected:
            folium.CircleMarker(
                location=coord, radius=10, color="#FFFFFF", weight=2.5,
                fill=True, fill_color=color, fill_opacity=1, tooltip=node,
                popup=folium.Popup(f"<b>{node}</b><br>Cluster: {cluster}", max_width=150)
            ).add_to(fmap)
            folium.Marker(coord, icon=folium.DivIcon(
                html=f'<div style="font-size:9px;font-weight:700;color:#111;'
                     f'text-shadow:0 0 3px #fff,-1px 0 #fff,0 1px #fff,1px 0 #fff,0 -1px #fff;'
                     f'white-space:nowrap;">{node}</div>',
                icon_size=(60, 14), icon_anchor=(30, -6)
            )).add_to(fmap)
        else:
            folium.CircleMarker(
                location=coord, radius=6, color=color, weight=1.5,
                fill=True, fill_color=color, fill_opacity=0.3, tooltip=node
            ).add_to(fmap)

    st_folium(fmap, width=None, height=530, returned_objects=[])

    legend_items = []
    CLUSTER_ORDER_LEGEND = ["S6", "S7", "S8", "S9", "S10"]
    for cl in CLUSTER_ORDER_LEGEND:
        c = CLUSTER_COLORS.get(cl, "#888")
        legend_items.append(
            f'<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
            f'<span style="width:12px;height:12px;border-radius:50%;background:{c};'
            f'border:2px solid #fff;box-shadow:0 0 0 1.5px {c};display:inline-block;flex-shrink:0;"></span>'
            f'<span style="font-size:0.75rem;font-weight:600;color:#4A4869;">{cl}</span></span>'
        )
    legend_items.append(
        '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
        '<span style="width:28px;height:3px;background:#6DA0E1;display:inline-block;border-radius:2px;"></span>'
        '<span style="font-size:0.75rem;color:#4A4869;">MST Edge</span></span>'
    )
    legend_items.append(
        '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
        '<span style="width:28px;height:4px;background:#5B61B2;display:inline-block;border-radius:2px;"></span>'
        '<span style="font-size:0.75rem;color:#4A4869;">Delivery Route</span></span>'
    )
    legend_items.append(
        '<span style="display:inline-flex;align-items:center;gap:5px;margin-right:14px;">'
        '<span style="width:28px;height:4px;background:#E63946;display:inline-block;border-radius:2px;"></span>'
        '<span style="font-size:0.75rem;color:#E63946;font-weight:600;">Priority Route</span></span>'
    )
    st.markdown(
        '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;'
        'background:#fff;border:1.5px solid #E4DCF0;border-radius:10px;'
        'padding:9px 14px;margin-top:6px;">'
        '<span style="font-family:DM Mono,monospace;font-size:0.62rem;font-weight:600;'
        'color:#9CA3AF;letter-spacing:0.08em;text-transform:uppercase;margin-right:10px;">Legend</span>'
        + "".join(legend_items) + '</div>', unsafe_allow_html=True
    )

with info_col:
    if not result:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;color:#9CA3AF;">
          <div style="font-family:'DM Serif Display',serif;font-size:2.5rem;color:#DEC1DB;letter-spacing:-0.02em;">Origami</div>
          <div style="font-size:0.95rem;font-weight:500;margin-top:16px;color:#4A4869;">No route calculated yet</div>
          <div style="font-size:0.82rem;margin-top:6px;color:#9CA3AF;">Select buildings from the sidebar and click <b>Calculate Optimal Route</b></div>
        </div>
        """, unsafe_allow_html=True)
    
    if result:
        k_cost = result["kruskal"]["f_cost"]
        p_cost = result["prim"]["f_cost"]
        selected_key = "kruskal" if algo_choice == "Kruskal" else "prim"
        k_bg = "#DEC1DB" if selected_key == "kruskal" else "#EEE2DF"
        p_bg = "#DEC1DB" if selected_key == "prim" else "#EEE2DF"
        
        st.markdown(f"""
        <div style="display:flex; gap:10px; margin-bottom:15px; align-items: stretch;">
            <div style="flex:1; display:flex; flex-direction:column; justify-content:space-between; background-color: {k_bg}; padding: 15px; border-radius: 8px; border: 2px solid {'#5B61B2' if selected_key == 'kruskal' else 'transparent'};">
                <h4 style="margin-top:0; margin-bottom:10px; color: #1C1B2E; font-family: 'DM Serif Display', serif; font-size: 1.25rem; font-weight: 400; letter-spacing: -0.01em; white-space: nowrap;">Kruskal's Route</h4>
                <p style="margin:0; font-size:1.1rem;">Total Distance: <b>{k_cost:,.1f} m</b></p>
            </div>
            <div style="flex:1; display:flex; flex-direction:column; justify-content:space-between; background-color: {p_bg}; padding: 15px; border-radius: 8px; border: 2px solid {'#5B61B2' if selected_key == 'prim' else 'transparent'};">
                <h4 style="margin-top:0; margin-bottom:10px; color: #1C1B2E; font-family: 'DM Serif Display', serif; font-size: 1.25rem; font-weight: 400; letter-spacing: -0.01em; white-space: nowrap;">Prim's Route</h4>
                <p style="margin:0; font-size:1.1rem;">Total Distance: <b>{p_cost:,.1f} m</b></p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <h3 style="font-family: 'DM Serif Display', serif; color: #5B61B2; margin-top: 10px; margin-bottom: 15px; font-weight: 400; letter-spacing: -0.01em;">
            Delivery Order &mdash; {algo_choice}
        </h3>
        """, unsafe_allow_html=True)
        
        active_route = result[selected_key]["f_route"]
        
        cumulative = 0
        route_rows = []
        for i, node in enumerate(active_route):
            seg = 0
            if i > 0:
                try: seg = get_strict_dist(active_route[i-1], node)
                except Exception: seg = 0
            cumulative += seg
            
            # Label priority nodes in the table
            is_urgent = "🚨 " if node in urgent_nodes else ""
            route_rows.append({
                "Stop": i+1, 
                "Node": is_urgent + node,
                "Cluster": nodes_info[node]["cluster"],
                "Seg (m)": seg, 
                "Total (m)": cumulative
            })

        df = pd.DataFrame(route_rows)
        def color_cluster(val):
            c = CLUSTER_COLORS.get(val, "#888")
            return f"background-color:{c}22; color:{c}; font-weight:700"

        styled = (df.style
                  .map(color_cluster, subset=["Cluster"])
                  .format({"Seg (m)": "{:,}", "Total (m)": "{:,}"})
                  .set_properties(**{"font-size": "0.78rem"}))

        st.dataframe(styled, use_container_width=True, height=320)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Export CSV", csv, "delivery_route.csv", "text/csv", use_container_width=True)
