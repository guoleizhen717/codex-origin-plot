# Origin plot recipes — combined tool cutting force analysis

> Ready-to-run recipes for the combined-tool cutting force analysis workflow.
> Each recipe assumes `references/origin_com_ref.md` has been read and Origin
> is running via COM.

---

## Recipe 1: Combined Tool Forces (Grouped Column Chart)

**When**: Show cutting/leading tool force comparison across penetration depths.

**Data layout** (in Origin workbook):
| Col A: Penetration(mm) | Col B: CuttingTool(N) | Col C: LeadingTool(N) |
|------------------------|----------------------|----------------------|
| 10 | 130.32 | 292.05 |
| 20 | 145.10 | 316.03 |
| 40 | 177.15 | 361.17 |
| 50 | 192.82 | 391.48 |

**LabTalk**:
```labtalk
plotxy iy:=(1,2) plot:=202 ogl:=[<new template:=Column>]
xb.text$ = "Penetration (mm)"
yl.text$ = "Cutting Force (N)"
layer.x.from = 0; layer.x.to = 65
layer.y.from = 0; layer.y.to = 700
label -s -sa -n title "(a) Combined Tool Forces"
```

**Key settings**:
- `plot:=202` = grouped column chart
- X-axis: 0–65 mm (leaves room for labels)
- Y-axis: 0–700 N

---

## Recipe 2: Cutting Specific Energy (Line + Symbol)

**When**: Show how specific energy decreases with penetration.

**Data layout**:
| Col A: Penetration(mm) | Col D: SE(N/mm) |
|------------------------|-----------------|
| 10 | 42.24 |
| 20 | 23.06 |
| 40 | 13.46 |
| 50 | 11.69 |

**LabTalk**:
```labtalk
plotxy iy:=(1,3) plot:=201 ogl:=[<new template:=LineSymb>]
xb.text$ = "Penetration (mm)"
yl.text$ = "Specific Energy (N/mm)"
layer.x.from = 0; layer.x.to = 65
layer.y.from = 0; layer.y.to = 55
label -s -sa -n title "(b) Cutting Specific Energy"
```

---

## Recipe 3: Synergistic Coefficient (Line + Symbol)

**When**: Show how K increases and approaches an asymptote.

**Data layout**:
| Col A: Penetration(mm) | Col E: K_coeff |
|------------------------|----------------|
| 10 | 0.4462 |
| 20 | 0.4591 |
| 40 | 0.4905 |
| 50 | 0.4925 |

**LabTalk**:
```labtalk
plotxy iy:=(1,4) plot:=201 ogl:=[<new template:=LineSymb>]
xb.text$ = "Penetration (mm)"
yl.text$ = "Synergistic Coefficient K"
layer.x.from = 0; layer.x.to = 65
layer.y.from = 0.40; layer.y.to = 0.55
label -s -sa -n title "(c) Synergistic Coefficient"
```

---

## Recipe 4: 3-Panel Merged Figure

**Merge 3 graphs into 1-column × 3-row layout**:
```labtalk
merge_graph option:=2 row:=3 col:=1 keepsize:=0
```

If `merge_graph` returns False via COM, create graphs in a single Python session
and export each individually (3 separate PNGs).

---

## Recipe 5: Custom multi-layer graph (no merge needed)

Create a single graph window with 3 vertical layers:
```labtalk
// Layer 1 (top): Forces
plotxy iy:=(1,2) plot:=202 ogl:=[<new template:=Column>]
// Add layers 2 and 3
layer -i 2  // insert layer below
layer -i 3  // insert another
// ... plot into each layer
```

More complex but avoids the `merge_graph` COM bug.

---

## Color and font conventions

For publication-grade output:
- Font: Arial or Times New Roman, 18 pt axis labels, 24 pt title
- Use consistent axis ranges across panels
- Export at 300 DPI minimum: `expGraph ... tr1.unit:=2` for pixel units
