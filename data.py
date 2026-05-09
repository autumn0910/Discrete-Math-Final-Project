"""
Dữ liệu bản đồ phân khu The Origami - Vinhomes Grand Park
===================================================================
Tọa độ GPS được estimate bằng phương pháp PIXEL MAPPING từ mặt bằng
tổng thể chính thức của chủ đầu tư Vinhomes.

Anchor points (ground truth từ Google Maps):
  - Góc Đường Phước Thiện (top-right map):   10.8505, 106.8196
  - Góc Vành Đai 3 (bottom-right map):        10.8445, 106.8196
  - Góc Rạch Bà Dì / Đ.An (bottom-left):     10.8445, 106.8108
  - Góc Phước Thiện / Nguyễn Xiển (top-left): 10.8505, 106.8108

Bounding box thực tế:
  lat: 10.8448 (Nam) → 10.8500 (Bắc)  ≈ 580m N-S
  lon: 106.8115 (Tây) → 106.8193 (Đông) ≈ 760m E-W

Thứ tự tọa độ: (latitude, longitude)
===================================================================
"""

CLUSTER_COLORS = {
    "S6":   "#FF6B35",
    "S7":   "#FFBE0B",
    "S8":   "#3A86FF",
    "S9":   "#8338EC",
    "S10":  "#1A936F",
    "Road": "#AAAAAA",
}

nodes_pos = {
    # Entrance chính (cổng phía Nam, Đường Anh Đào)
    "Entrance_Main":    (10.8450, 106.8150),

    # Giao lộ nội khu (Đường Anh Đào các nhánh)
    "Inters_S6_S7":     (10.8458, 106.8143),
    "Inters_S7_S8":     (10.8465, 106.8128),
    "Inters_S8_S9":     (10.8478, 106.8128),
    "Inters_S9_S10":    (10.8487, 106.8152),
    "Inters_S10_East":  (10.8490, 106.8178),

    # Cluster S6 - góc Đông Nam, cạnh CV Cầu Vồng & Vành Đai 3
    "S6.01":  (10.8451, 106.8160),
    "S6.02":  (10.8454, 106.8153),
    "S6.03":  (10.8460, 106.8148),
    "S6.05":  (10.8458, 106.8170),
    "S6.06":  (10.8455, 106.8177),

    # Cluster S7 - trung tâm phía Nam
    "S7.01":  (10.8458, 106.8137),
    "S7.02":  (10.8461, 106.8127),
    "S7.03":  (10.8464, 106.8137),
    "S7.05":  (10.8462, 106.8145),

    # Cluster S8 - phía Tây, giáp Rạch Bà Dì
    "S8.01":  (10.8463, 106.8120),
    "S8.02":  (10.8470, 106.8115),
    "S8.03":  (10.8478, 106.8115),

    # Cluster S9 - trung tâm phía Bắc
    "S9.01":  (10.8480, 106.8133),
    "S9.02":  (10.8487, 106.8123),
    "S9.03":  (10.8484, 106.8143),

    # Cluster S10 - góc Đông Bắc, mặt tiền Phước Thiện & Vành Đai 3
    "S10.01": (10.8483, 106.8168),
    "S10.02": (10.8488, 106.8155),
    "S10.03": (10.8490, 106.8180),
    "S10.05": (10.8496, 106.8170),
    "S10.06": (10.8492, 106.8162),
    "S10.07": (10.8498, 106.8182),
}

nodes_info = {
    "Entrance_Main":   {"cluster": "Road"},
    "Inters_S6_S7":    {"cluster": "Road"},
    "Inters_S7_S8":    {"cluster": "Road"},
    "Inters_S8_S9":    {"cluster": "Road"},
    "Inters_S9_S10":   {"cluster": "Road"},
    "Inters_S10_East": {"cluster": "Road"},
    "S6.01":  {"cluster": "S6"}, "S6.02":  {"cluster": "S6"},
    "S6.03":  {"cluster": "S6"}, "S6.05":  {"cluster": "S6"},
    "S6.06":  {"cluster": "S6"},
    "S7.01":  {"cluster": "S7"}, "S7.02":  {"cluster": "S7"},
    "S7.03":  {"cluster": "S7"}, "S7.05":  {"cluster": "S7"},
    "S8.01":  {"cluster": "S8"}, "S8.02":  {"cluster": "S8"},
    "S8.03":  {"cluster": "S8"},
    "S9.01":  {"cluster": "S9"}, "S9.02":  {"cluster": "S9"},
    "S9.03":  {"cluster": "S9"},
    "S10.01": {"cluster": "S10"}, "S10.02": {"cluster": "S10"},
    "S10.03": {"cluster": "S10"}, "S10.05": {"cluster": "S10"},
    "S10.06": {"cluster": "S10"}, "S10.07": {"cluster": "S10"},
}

raw_edges = [
    # Backbone đường Anh Đào nội khu
    ["Entrance_Main",   "Inters_S6_S7",    200],
    ["Inters_S6_S7",    "Inters_S7_S8",    240],
    ["Inters_S7_S8",    "Inters_S8_S9",    150],
    ["Inters_S8_S9",    "Inters_S9_S10",   320],
    ["Inters_S9_S10",   "Inters_S10_East", 250],

    # S6 internal
    ["S6.01", "S6.02", 120],
    ["S6.02", "S6.03", 100],
    ["S6.03", "S6.05", 220],
    ["S6.05", "S6.06",  80],
    ["S6.01", "S6.06", 160],
    # S6 <-> road
    ["S6.01", "Entrance_Main",   130],
    ["S6.02", "Entrance_Main",    80],
    ["S6.03", "Inters_S6_S7",   100],
    ["S6.05", "Inters_S10_East", 300],

    # S7 internal
    ["S7.01", "S7.02", 130],
    ["S7.02", "S7.03", 150],
    ["S7.03", "S7.05", 110],
    ["S7.01", "S7.05",  90],
    # S7 <-> road
    ["S7.01", "Inters_S6_S7",  90],
    ["S7.05", "Inters_S6_S7",  80],
    ["S7.02", "Inters_S7_S8", 120],
    ["S7.03", "Inters_S7_S8", 100],

    # S8 internal
    ["S8.01", "S8.02", 140],
    ["S8.02", "S8.03", 160],
    # S8 <-> road
    ["S8.01", "Inters_S7_S8", 100],
    ["S8.02", "Inters_S7_S8", 110],
    ["S8.03", "Inters_S8_S9", 120],

    # S9 internal
    ["S9.01", "S9.02", 150],
    ["S9.01", "S9.03", 130],
    ["S9.02", "S9.03", 200],
    # S9 <-> road
    ["S9.01", "Inters_S8_S9",  120],
    ["S9.02", "Inters_S8_S9",  160],
    ["S9.03", "Inters_S9_S10", 130],

    # S10 internal
    ["S10.01", "S10.02", 150],
    ["S10.02", "S10.06", 110],
    ["S10.06", "S10.05", 100],
    ["S10.05", "S10.07", 130],
    ["S10.01", "S10.03", 130],
    ["S10.03", "S10.07", 110],
    ["S10.05", "S10.03", 150],
    # S10 <-> road
    ["S10.01", "Inters_S9_S10",   170],
    ["S10.02", "Inters_S9_S10",    90],
    ["S10.05", "Inters_S10_East", 160],
    ["S10.07", "Inters_S10_East", 120],
]


def get_graph_data():
    return nodes_pos, raw_edges, nodes_info
