import random

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from sym_cps.grammar import Grammar
from sym_cps.grammar.rules import generate_random_topology, generate_random_new_topology
from sym_cps.representation.design.abstract import AbstractDesign
from sym_cps.shared.paths import grammar_rules_processed_path
import imageio
from sym_cps.tools.my_io import save_to_file


def create_frame(figure: Figure, title: str, iter: int):
    figure.savefig(f'./designs/{iter}.png', transparent=True)
    plt.close(figure)

def gen_designs():

    for i in range(200):
        print(f"Random iteration {i}")
        design_tag = f"grammar_plot_{50}"
        design_index = i

        new_design: AbstractDesign = generate_random_new_topology(
            design_tag=design_tag,
            design_index=design_index,
            max_right_num_wings=4,
            max_right_num_rotors=5,
        )

        create_frame(figure=new_design.plot, title=f"{i}", iter=i)

gen_designs()
frames = []
for i in range(50):
    image = imageio.v2.imread(f'./designs/{i}.png')
    frames.append(image)

imageio.mimsave(f'./designs.gif',
                frames,
                fps=5)
