# sym-cps

**Symbiotic Design for Cyber Physical Systems**

Project description available [here](https://www.darpa.mil/program/symbiotic-design-for-cyber-physical-systems)

Documentation available [here](https://uc-berkeley-data-discovery-2022.github.io/berkeley-cps-symbiotic-design/)


## Installation

### System Requirements

1. [pdm](https://github.com/pdm-project/pdm)
2. [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
3. Access to the `INPUT` folder on Google Drive.
   1. Copy `data` and `output` directories in the root of the repo

### Dependencies

To install the dependencies and environment, simply run:

```bash
make setup
```

The setup script will:
* Pull the submodules
* Install dependencies via pdm
* Create a new conda environment and install the conda dependencies


### Activate conda

Once script terminates successfully you can activate the environment:

```bash
conda activate ./.venv
```

### Configure AWS

1. Download the `aws-cvpn-config.ovpn` configuration file from the `INPUT` folder on Google Drive and use it to connect to the AWS VPN. Here are the instructions for [Linux](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/linux.html), [MacOS](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/macos.html) and [Windows](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/windows.html).
2. Create `./output/aws` if it does not exist already.
    1. (Optional) notify your IDE to _exclude_ the `aws` folder from being indexed. For example in PyCharm do `Right Click on aws - Mark directory as - Excluded`
3. Mount the shared folder in `./output/aws`. Instructions [here](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/mount-openzfs-volumes.html).
    1. Suggestion: from the root folder of the repo, you can try one of the following commands, according to your OS and preferences
        1. `sudo mount -t nfs 10.0.137.113:/fsx/ ./output/aws`
        2. `sudo mount_nfs -o resvport 10.0.137.113:/fsx/ ./output/aws`
4. After have successfully installed the dependencies and activated the conda environment. Launch the following command from the root of the repo 
```bash
pdm run suam-config install --no-symlink --input=./data/broker.conf.yaml
```



## Examples

Check the example folder and look at the code of the python files to get familiar with the API. Here's some example you can launch.

Populate the library of components from the `data` folder
```bash
python src/sym_cps/examples/library.py
```

Extracts the _seed designs_
```bash
python src/sym_cps/examples/designs.py
```

Create a new design from scratch. First choosing and topology and then concretize it.
```bash
python src/sym_cps/examples/topology.py
```


Evaluate designs
```bash
python src/sym_cps/examples/evaluation.py
```


## Troubleshooting

> NOTE:

If you have problems with the environment you can clean up the files and folders created by pdm and conda by running

```bash
make uninstall
```

Then try `make setup` again.




> NOTE:
> Install 
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


> NOTE:
> Problems installing dependencies
>
> Look at the setup script located in `scripts/setup.sh` and launch the commands individually. 
>
> You can make a clean installation by first running `make uninstall` and then `make setup` again.

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