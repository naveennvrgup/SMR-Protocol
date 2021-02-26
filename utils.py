from my_constants import time_quanta


def visualise_mesh(plt, all_vessels):
    n = len(all_vessels)

    for i in range(n):
        node = all_vessels[i]
        for nei in node.neighbours:
            plt.plot(
                [node.x, nei.x],
                [node.y, nei.y]
            )


def visualise_adj(plt, all_vessels):
    n = len(all_vessels)
    lines = []

    for i in range(n):
        node = all_vessels[i]

        for _ in range(len(lines)):
            plt_line = lines.pop()
            plt_line.pop().remove()

        for nei in node.neighbours:
            lines.append(plt.plot(
                [node.x, nei.x],
                [node.y, nei.y],
                'blue'
            ))

        plt.pause(time_quanta)


def paint_debug_point(plt, x, y):
    point = plt.scatter(x, y, s=60, facecolors='b')
    