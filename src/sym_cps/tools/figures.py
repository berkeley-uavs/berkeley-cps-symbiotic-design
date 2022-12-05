import numpy as np


def plot_3d_grid(node_xyz: np.array, color_xyz: np.array, ):

    # Extract node and edge positions from the layout
    node_xyz = np.array([graph.nodes[v]["position"] for v in sorted(graph)])
    color_xyz = np.array([graph.nodes[v]["color"] for v in sorted(graph)])

    edge_xyz = np.array([(graph.nodes[u]["position"], graph.nodes[v]["position"]) for u, v in graph.edges()])

    # Create the 3D figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # Plot the nodes - alpha is scaled by "depth" automatically
    ax.scatter(*node_xyz.T, s=100, ec="w", c=color_xyz)

    # Plot the edges
    for vizedge in edge_xyz:
        ax.plot(*vizedge.T, color="tab:gray")

    # Turn gridlines off
    ax.grid(False)
    # Suppress tick labels
    for dim in (ax.xaxis, ax.yaxis, ax.zaxis):
        dim.set_ticks([])
    # Set axes labels
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    fig.tight_layout()
    # fig.show()
    return fig