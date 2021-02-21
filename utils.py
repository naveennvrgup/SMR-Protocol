def visualise_adj(plt, all_vessels, adj):
    n = len(all_vessels)

    for i in range(n):
        node = all_vessels[i]
        for nei in adj[i]:
            plt.plot(
                [node.x, nei.x],
                [node.y, nei.y]
            )
