# sym-cps

**Symbiotic Design for Cyber Physical Systems**

Project description available [here](https://www.darpa.mil/program/symbiotic-design-for-cyber-physical-systems)

Documentation available [here](https://uc-berkeley-data-discovery-2022.github.io/berkeley-cps-symbiotic-design/)


## Installation

### System Requirements

1. [pdm](https://github.com/pdm-project/pdm)
2. Access to [this repo](https://github.com/uc-berkeley-data-discovery-2022/swri_data).
   1. Copy `data`, `fdm`, and `output` directories in the root of the repo
   2. Keep data and output updated if there are changes on the Google Drive

### Dependencies

1. Update the submodules
    ```bash
    git submodule init
    git submodule update --
    ```
    Make sure that `eval_pipeline` folder is not empty. 
    If the submodule was not pulled correctly you can simply clone [this](https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git) repo and copy its content inside `eval_pipeline` folder.
2. Install
    ```bash
    pdm install
    ```

### Configure AWS

1. Download the `aws-cvpn-config.ovpn` configuration file from the `INPUT` folder on Google Drive and use it to connect to the AWS VPN. Here are the instructions for [Linux](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/linux.html), [MacOS](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/macos.html) and [Windows](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/windows.html).
2. Create the folder `./output/aws` if it does not exist already.
    1. (Optional) notify your IDE to _exclude_ the `aws` folder from being indexed. For example in PyCharm do `Right Click on aws - Mark directory as - Excluded`
3. Mount the shared folder in `./output/aws`. Instructions [here](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/mount-openzfs-volumes.html). Make sure you are connected via the VPN before mounting the shared drive.
    1. Suggestion: from the root folder of the repo, you can try one of the following commands, according to your OS and preferences
        1. `sudo mount -t nfs 10.0.137.113:/fsx/ ./output/aws`
        2. `sudo mount_nfs -o resvport 10.0.137.113:/fsx/ ./output/aws`
        3. `sudo mount -o resvport -t nfs 10.0.137.113:/fsx/ ./output/aws`
4. After have successfully installed the dependencies and activated the conda environment. Launch the following command from the root of the repo 
```bash
sudo pdm run suam-config install --no-symlink --input=./data/broker.conf.yaml
```

### Run

#### Launch Python scripts from command line

When running a python script from command line, insert `pdm run` before. For example:

```bash
pdm run python src/sym_cps/examples/library.py
```


#### Working with IDEs

With PEP 582, dependencies will be installed into __pypackages__ directory under the project root. With PEP 582 enabled globally, you can also use the project interpreter to run scripts directly.
Check [pdm documentation](https://pdm.fming.dev/latest/usage/pep582/) on PEP 582.


**PYCHARM**
Add `__pypackages__/3.10/lib` and `src` folders to your PYTHONPATH. With PyCharm you can simple right click on the folders and select `Mark Directory as` - `Source folder`.

**VSCODE**

To configure VSCode to support PEP 582, open `.vscode/settings.json` (create one if it does not exist) and add the following entries:
```json
{
  "python.autoComplete.extraPaths": ["__pypackages__/3.10/lib"],
  "python.analysis.extraPaths": ["__pypackages__/3.10/lib"]
}
```


## Useful scripts

*   Uninstall all dependencies and clean up the repository from temporary files
    ```bash
    make uninstall
    ```

*   Load library and seed designs and export them in the output folder
    ```bash
    pdm run initialize
    ```

*   Export all seed designs in the output folder
    ```bash
    pdm run export-designs
    ```
    
*   Load and export custom design where "custom_design_file" is the file name of the `json` file in the `data/custom_designs` folder
    ```bash
    pdm run custom-design "custom_design_file"
    ```


## Examples

Check the example folder and look at the code of the python files to get familiar with the API. Here's some example you can launch.

Populate the library of components from the `data` folder
```bash
pdm run python src/sym_cps/examples/library.py
```

Extracts the _seed designs_
```bash
pdm run python src/sym_cps/examples/designs.py
```

Create a new design from scratch. First choosing and topology and then concretize it.
```bash
pdm run python src/sym_cps/examples/topology.py
```


Evaluate designs from command line specifying the path of the `design_swri,json` in `<design-file>`:
```bash
sudo pdm run suam-client direct2cad.process-design --design=<design-file> --results=./output/aws/results
```

For example:
```bash
pdm run suam-client direct2cad.process-design --design=./output/designs/TestQuad/design_swri.json --results=./output/aws/results
```


Evaluate designs from python
```bash
pdm run python src/sym_cps/examples/evaluation.py
```


## Web interface

Run the back-end by executing `backend/app.py`

Install react dependencies via npm by running:

```bash
npm install --legacy-peer-deps
```

inside the `frontend` folder.

Then run the front-end:

```bash
npm run start
```




## Troubleshooting

NOTE:

If you have problems with the environment you can clean up the files and folders created by pdm and conda by running

```bash
make uninstall
```

Then try installation process again.



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


For Mac M1 users, change the architecture first by running:
```bash
env /usr/bin/arch -x86_64 /bin/zsh --login
```


> NOTE: Apple Silicon
> Make sure that you are running python3 for Apple Silicon and not the Intel version otherwise pdm will pull the packages for the wrong architecture
> You can uninstall python via brew by running and try install the repository again
> ```bash
> brew uninstall --ignore-dependencies python
> ```
> If you still have problems you can run a x86 terminal commands with Apple’s Rosetta 2 by launching:
>
> ```bash
> arch -x86_64 /bin/bash
> ```
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
> 
> Go to Preferences/Tools/Terminal and set the shell path to be:
> ```bash
> env /usr/bin/arch -x86_64 /bin/zsh --login
> ```



## License

[MIT](https://github.com/piergiuseppe/sym-cps/blob/master/LICENSE)

## Features and Credits

- Fully typed with annotations and checked with mypy,
  [PEP561 compatible](https://www.python.org/dev/peps/pep-0o561/)
  
  
  