import random

import imageio
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from sym_cps.grammar import Grammar
from sym_cps.shared.paths import grammar_rules_processed_path


def create_frame(figure: Figure, title: str, iter: int):
    # figure.title(f'{title}',
    #              fontsize=14)
    figure.savefig(f"./img/{title}_{iter}.png", transparent=True)
    plt.close(figure)


if __name__ == '__main__':
    grammar = Grammar.from_json(rules_json_path=grammar_rules_processed_path)

    for ri, rule in enumerate(grammar.rules):
        conditions = rule.conditions.get_all_conditions()
        selection = random.choices(conditions, k=10)
        for i, condition in enumerate(conditions):
            create_frame(figure=condition.plot, title=f"{rule.name}", iter=i)
        frames = []
        for t in range(len(conditions)):
            image = imageio.v2.imread(f"./img/{rule.name}_{t}.png")
            frames.append(image)

        # imageio.mimsave(f"./{rule.name}{ri}.gif", frames, fps=5)
