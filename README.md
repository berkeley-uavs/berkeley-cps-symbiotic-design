# sym-cps

**Symbiotic Design for Cyber Physical Systems**

Project description available [here](https://www.darpa.mil/program/symbiotic-design-for-cyber-physical-systems)

Documentation available [here](https://uc-berkeley-data-discovery-2022.github.io/berkeley-cps-symbiotic-design/)


## Updates October 22

Make sure that in your `eval_pipeline` there is [this](https://github.com/LOGiCS-Project/swri-simple-uam-pipeline/tree/features/oct-22-fdm-update) branch. If you have problems with the submodule, just clone it inside `eval_pipeline`.


## Local Installation

### System Requirements

1. [pdm](https://github.com/pdm-project/pdm)
2. Access to [this repo](https://github.com/uc-berkeley-data-discovery-2022/challenge_data).

### Quick start

1. Clone the two repos and their submodules in the same folder

    ```bash
    git clone --recurse-submodules https://github.com/uc-berkeley-data-discovery-2022/berkeley-cps-symbiotic-design.git
    ```
   
    ```bash
    git clone https://github.com/uc-berkeley-data-discovery-2022/challenge_data.git
    ```
   
2. Navigate to `berkeley-cps-symbiotic-design` folder and install dependencies

    ```bash
    cd berkeley-cps-symbiotic-design
    ```
   You don't have to create a virual environment with pdm, you can launch the command:
    ```bash
    pdm config python.use_venv false
    ```
   
   and then
    ```bash
    pdm install
    ```

### Configure AWS

1. Download the `aws-cvpn-config.ovpn` configuration file from the [challenge_data repo](https://github.com/uc-berkeley-data-discovery-2022/challenge_data) repo and use it to connect
   to the AWS VPN. Here are the instructions
   for [Linux](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/linux.html)
   , [MacOS](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/macos.html)
   and [Windows](https://docs.aws.amazon.com/vpn/latest/clientvpn-user/windows.html).
2. Create the folder `../challenge_data/aws` if it does not exist already.
    1. (Optional) notify your IDE to _exclude_ the `aws` folder from being indexed. For example in PyCharm
       do `Right Click on aws - Mark directory as - Excluded`
3. Mount the shared folder in `../challenge_data/aws`.
   Instructions [here](https://docs.aws.amazon.com/fsx/latest/OpenZFSGuide/mount-openzfs-volumes.html). Make sure you
   are connected via the VPN before mounting the shared drive.
    1. Suggestion: from the root folder of the repo, you can try one of the following commands, according to your OS and
       preferences
        1. `sudo mount -t nfs 10.0.137.113:/fsx/ ../challenge_data/aws`
        2. `sudo mount_nfs -o resvport 10.0.137.113:/fsx/ ../challenge_data/aws`
        3. `sudo mount -o resvport -t nfs 10.0.137.113:/fsx/ ../challenge_data/aws`
4. After have successfully installed the dependencies and activated the conda environment. Launch the following command
   from the root of the repo

    ```bash
    sudo pdm run suam-config install --no-symlink --input=../challenge_data/data/broker.conf.yaml
    ```


## Docker Installation

### System Requirements

1. [Docker](https://docs.docker.com/engine/install/)
2. Access to [this repo](https://github.com/uc-berkeley-data-discovery-2022/challenge_data).


### Quick start

1. Clone the two repos and their submodules in the same folder

    ```bash
    git clone --recurse-submodules https://github.com/uc-berkeley-data-discovery-2022/berkeley-cps-symbiotic-design.git
    ```
   
    ```bash
    git clone https://github.com/uc-berkeley-data-discovery-2022/challenge_data.git
    ```
   
2. Navigate to `berkeley-cps-symbiotic-design` folder and launch docker script.

    ```bash
    cd berkeley-cps-symbiotic-design & \
    ./docker_run.sh bash
    ```

You can now launch the scripts and the python files. For example:

  ```bash
  pdm run init
  ```
To initialize the library of components and seed design

  ```bash
  pdm run custom-design "working/test_quad_abstraction_3"
  ```
To generate a custom design from json file (this script does not send it to evaluation)

  ```bash
  pdm run evaluate "test_quad_cargo"
  ```
To generate a custom design from json file, send it to evaluation and retrieve the results. 
The results appear in the `challenge_data/output/<DESIGN_NAME>` automatically (a json file with the evaluation results and an STL file with the 3D model).

Any change you make to the files in `berkeley-cps-symbiotic-design` will be immediately available inside the docker container. 


### Remote deployment from IDE

The docker image contains an ssh server that you can connect from your IDE and run your code/debug directly inside docker without the need of installing any dependencies.

Launch:
```bash
  ./docker_run.sh
```
to launch the docker image as a new container running in background.

Then connect to the python interpreter via SSH on port 9922 of localhost as explained below:

#### PyCharm


* Go to:  `Preference > Build, Execution… > Deployment`
* Add new `SFTP`. 
* Give a name, e.g. : `docker-sym-cps`.
* Add a new SSH configuration:
    * Host: localhost
    * Port: 9922
    * Username: root
    * Password: password
    * Root path: `/root`
* Mappings: 
    * Local path ‘<LOCAL_PATH>/berkeley-cps-symbiotic-design’
    * Deployment path ‘/ide’


Got to: `Preferences > Project… > Python Interpreter > Add Interpreter > On SSH` and select  Existing Connection the SSH connection previously created, then select the “System Interpreter” as Python runtime configuration, i.e. the interpreter at `/usr/bin/python3’.  “Sync folders”  insert `<Project root>→/root/ide`

On `Python Interpreter`, click on `Show all` and select the Remote Python interpreter that you have just created. On the top right of the window clock on  __Show Interpreter Paths__, and add a new path `/root/host/__pypackages__/3.10/lib`.



## Run

#### Launch Python scripts from command line

When running a python script from command line, insert `pdm run` before. For example:

```bash
pdm run python src/sym_cps/examples/library.py
```

<<<<<<< HEAD
### Run

#### Launch Python scripts from command line

When running a python script from command line, insert `pdm run` before. For example:

```bash
pdm run pdm run python src/sym_cps/examples/library.py
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


=======
#### Working with IDEs

With PEP 582, dependencies will be installed into __pypackages__ directory under the project root. With PEP 582 enabled
globally, you can also use the project interpreter to run scripts directly.
Check [pdm documentation](https://pdm.fming.dev/latest/usage/pep582/) on PEP 582.

**PYCHARM**
Add `__pypackages__/3.10/lib` and `src` folders to your PYTHONPATH. With PyCharm you can simple right click on the
folders and select `Mark Directory as` - `Source folder`.

**VSCODE**

To configure VSCode to support PEP 582, open `.vscode/settings.json` (create one if it does not exist) and add the
following entries:

```json
{
  "python.autoComplete.extraPaths": [
    "__pypackages__/3.10/lib"
  ],
  "python.analysis.extraPaths": [
    "__pypackages__/3.10/lib"
  ]
}
```

## Useful scripts

* Uninstall all dependencies and clean up the repository from temporary files
  ```bash
  make uninstall
  ```

* Load library and seed designs and export them in the output folder
  ```bash
  pdm run init
  ```

* Export all seed designs in the output folder
  ```bash
  pdm run export-designs
  ```

* Load and export custom design where "custom_design_file" is the file name of the `json` file in
  the `data/custom_designs` folder, for example:
  ```bash
  pdm run custom-design "working/test_quad_abstraction_3"
  ```
>>>>>>> main

## Examples

Check the example folder and look at the code of the python files to get familiar with the API. Here's some example you
can launch.

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
sudo pdm run suam-client direct2cad.process-design --design=<design-file> --results=../challenge_data/aws/results
```

For example:

```bash
pdm run suam-client direct2cad.process-design --design=../challenge_data/output/designs/TestQuad/design_swri.json --results=../challenge_data/aws/results
```

Evaluate designs from python
<<<<<<< HEAD
```bash
pdm run python src/sym_cps/examples/evaluation.py
```
=======
>>>>>>> main

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

### Installation process

If you have problems with the environment you can clean up the files and folders created by pdm and conda by running
```bash
make uninstall
```
Then try installation process again.
```bash
pdm install
```

### Submodules
Make sure the submodules are correctly imported and updated
```bash
git submodule init
git submodule update --
```
Make sure that `eval_pipeline` folder is not empty.
If the submodule was not pulled correctly you can simply
clone [this](https://github.com/LOGiCS-Project/swri-simple-uam-pipeline.git) repo and copy its content
inside `eval_pipeline` folder.


### Apple Silicon

<<<<<<< HEAD
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
=======
For Mac M1 users, if you have architecture problems (i.e. some packages are not available for arm), you can try simulating x86_64 architecture and install the dependencies again.
```bash
env /usr/bin/arch -x86_64 /bin/zsh
```
However, all the dependencies right now should support arm and you should not change architecture.

To run a x86 terminal by default in VSCode, add the following to your `settings.json`
```json
"terminal.integrated.profiles.osx": {
   "x86 bash": {
       "path": "/usr/bin/arch",
       "args": ["-arch", "x86_64", "/bin/bash"]
   }},
"terminal.integrated.defaultProfile.osx": "x86 bash"
```
>>>>>>> main

To run a x86 terminal by default in PyCharm, go to Preferences/Tools/Terminal and set the shell path to be:

<<<<<<< HEAD

> NOTE: Apple Silicon
> Make sure that you are running a x86 terminal.
> You can run x86 terminal commands with Apple’s Rosetta 2 by launching:
>
> ```bash
> arch -x86_64 /bin/bash
> ```
> 


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
=======
```bash
env /usr/bin/arch -x86_64 /bin/zsh --login
```
>>>>>>> main

## Features and Credits

Fully typed with annotations and checked with mypy, [PEP561 compatible](https://www.python.org/dev/peps/pep-0o561/)
  
  
  