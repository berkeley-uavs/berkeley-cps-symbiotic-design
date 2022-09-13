# sym-cps

**Symbiotic Design for Cyber Physical Systems**

Project description available [here](https://www.darpa.mil/program/symbiotic-design-for-cyber-physical-systems)

Documentation available [here](https://logics-project.github.io/berkeley-cps-symbiotic-design/)


## Installation

We use [pdm](https://github.com/pdm-project/pdm) to most of the dependencies, and
[conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html). Make sure they are installed on your system.

To install the environment, simply run:

```bash
make setup
```

The setup script will:
* Install all the dependecies via pdm
* Create a new conda environment and isntall the conda dependencies

Once the dependencies are installed you can activate the environments and launching python scripts.

If you have problems with the environment you can clean up the files and folders created by pdm and conda by running

```bash
make uninstall
```

Then try `make setup` again.



### Activating conda enviornment

```bash
conda activate ./.venv
```

### Launch examples

```bash
python src/sym_cps/examples/library.py
```

```bash
python src/sym_cps/examples/designs.py
```

```bash
python src/sym_cps/examples/topology.py
```

Check the example folder for more examples. Look at the code in the examples to understand the APIs available.


### Documentation
```bash
make docs-serve
```


## Troubleshooting

> NOTE:
> If it fails for some reason,
> you'll need to install
> [PDM](https://github.com/pdm-project/pdm)
> manually.
>
> You can install it with:
>
> ```bash
> python3 -m pip install --user pipx
> pipx install pdm
> ```
>
> Now you can try running `make setup` again.

> NOTE: Apple Silicon
> Make sure that you are running a x86 terminal.
> You can run x86 terminal commands with Apple’s Rosetta 2 by launching:
>
> ```bash
> arch -x86_64 /bin/bash
> ```

> NOTE: Conda for Mac with Apple Silicon
>
> Some of the packages in conda do not support arm64 architecture. To install all the dependencies correctly on a Mac with Apple Silicon, make sure that you are running conda for x86_64 architecture.
>
> You can install miniconda for MacOSX x86_64 by running the following commands
>
> ```bash
> curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh > Miniconda3-latest-MacOSX-x86_64.sh
> ```
>
> ```bash
> sh Miniconda3-latest-MacOSX-x86_64.sh
> ```



> NOTE: Working with PEP 582
> With PEP 582, dependencies will be installed into __pypackages__ directory under the project root. With PEP 582 enabled globally, you can also use the project interpreter to run scripts directly.
> Check [pdm documentation](https://pdm.fming.dev/latest/usage/pep582/) on PEP 582.
> To configure VSCode to support PEP 582, open `.vscode/settings.json` (create one if it does not exist) and add the following entries:
> ```json
> {
>   "python.autoComplete.extraPaths": ["__pypackages__/3.10/lib"],
>   "python.analysis.extraPaths": ["__pypackages__/3.10/lib"]
> }
> ```

> NOTE: VSCode and Apple Silicon
> To run a x86 terminal by default in VSCode. Add the following to your `settings.json`
> ```json
> "terminal.integrated.profiles.osx": {
>    "x86 bash": {
>        "path": "/usr/bin/arch",
>        "args": ["-arch", "x86_64", "/bin/bash"]
>    }
>},
>"terminal.integrated.defaultProfile.osx": "x86 bash"
> ```

> NOTE: PyCharm and Apple Silicon
> Go to Preferences/Tools/Terminal and set the shell path to be:
>  ```bash
>  env /usr/bin/arch -x86_64 /bin/zsh --login
> ```



## License

[MIT](https://github.com/piergiuseppe/sym-cps/blob/master/LICENSE)

## Features and Credits

- Fully typed with annotations and checked with mypy,
  [PEP561 compatible](https://www.python.org/dev/peps/pep-0o561/)