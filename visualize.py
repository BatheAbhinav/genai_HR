from app.graph.workflow import policy_graph

# Print as Mermaid diagram
print(policy_graph.get_graph().draw_mermaid())

# Or ASCII art
print(policy_graph.get_graph().draw_ascii())