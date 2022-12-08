from src.graph import Graph
from src.autosched import sched_enum
from src.graph_config import graph_constants

if __name__ == "__main__":
  accesses = {
  'X': ['i', 'm'],
  'A': ['i', 'j'],
  'B': ['j', 'k'],
  'C': ['k', 'l'],
  'D': ['l', 'm']
  }
  schedules = sched_enum(['A', 'B', 'C', 'D'], accesses['X'], accesses)
  schedules_ = schedules

  g = Graph(height="1500px", width="100%", bgcolor="#222222", font_color="black", directed=True, schedules=schedules_, accesses=accesses)

  if graph_constants["ENABLE_BUTTONS"]:
    g.show_buttons()
  g.options.__dict__.update({
    "edges": {
      "color": {
        "color": "#BC90FD",
        "highlight": "#802CFB",
        "hover": "#802CFB"
      },
      "selectionWidth": 75,
      "hoverWidth": 50
    },
    "nodes": {
      "font": {
        "size": 50
      }
    },
    "interaction": {
      "hover": True
    }
  })
  if graph_constants["PLOT_REPULSION"]:
    g.repulsion(node_distance=6000, central_gravity=.01, spring_length=2500, spring_strength=.02)
  else:
    g.barnes_hut(central_gravity=.8, gravity=-30000, overlap=1, spring_length=2500, spring_strength=.0001, 
                damping=.2)

  if graph_constants["PLOT"]:
    g.show(graph_constants["OUTPUT_FILE"])
  