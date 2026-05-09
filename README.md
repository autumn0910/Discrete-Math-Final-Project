# Origami Delivery Optimizer

**MATH202 – Discrete Mathematics · Final Project**
Fulbright University Vietnam

> An interactive web application that models the Origami residential area (Vinhomes Grand Park) as a mathematical graph and computes the optimal delivery route using Minimum Spanning Tree algorithms.

🔗 **Live demo:** https://delivery-optimizer-vinhomesgrandpark.streamlit.app/

---

## Project Overview

Delivery personnel in large residential complexes face complex routing problems. This project applies discrete mathematics — specifically graph theory and MST algorithms — to minimize total travel distance across selected buildings in The Origami (clusters S6–S10).

The system allows a user to select any subset of buildings, then automatically computes and compares two MST-based delivery routes using **Kruskal's** and **Prim's** algorithms, displaying the optimal path on an interactive map.

---

## Algorithms

| Algorithm | Approach | Time Complexity |
|-----------|----------|-----------------|
| Kruskal's | Sort all edges by weight, add greedily avoiding cycles | O(E log E) |
| Prim's    | Grow MST from a start node by always picking the cheapest edge | O(E log V) |

Both algorithms guarantee a **Minimum Spanning Tree** — a connected subgraph with no cycles and minimum total edge weight — which forms the backbone of the optimal delivery route.

The delivery route is then derived from a **DFS traversal** of the MST, starting from the selected entry point.

---

## Tech Stack

| Layer | Library |
|-------|---------|
| Web UI | Streamlit |
| Graph computation | NetworkX |
| Interactive map | Folium + streamlit-folium |
| Data handling | Pandas |

---

## Project Structure

```
├── app.py            # Main Streamlit application & UI
├── algorithm.py      # MST computation and DFS routing logic
├── data.py           # Node coordinates and edge data (S6–S10)
├── requirements.txt  # Python dependencies
└── README.md
```

---

## How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## How to Use

1. Select buildings to deliver to from the sidebar (clusters S6–S10)
2. Choose a start point (default: `Entrance_Main`)
3. Click **Calculate Optimal Route**
4. The map displays the MST edges and delivery route
5. The panel on the right compares Kruskal vs Prim and shows the stop-by-stop breakdown

---

## Sample Results

- The app computes MST weight and full route distance for both algorithms
- The better algorithm (lower route distance) is highlighted automatically
- Results can be exported as CSV

---

## Team
Tran Hoang Phi Bao &
Nguyen Phuc Minh Anh

**Course:** MATH202 – Discrete Mathematics
**Semester:** Spring 2026
