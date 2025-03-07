# cdb_cellmaps

This is the sdk for integrating new tools (we call Service independent build blocks (SIBs)) for Cinco De Bio to work with cellmaps domain specific workflow language.

---

## Installation

```bash
pip install cdb_cellmaps
```

---

## Usage

### Command Line Interface

The library provides a command line interface with a few options to help you get started.

#### Help

```bash
cdb_cellmaps --help # for help
```

#### Init

```bash
cdb_cellmaps init <YourSibName> <ProcessConcept> # to generate all the boilerplate
cdb_cellmaps init <YourSibName> <ProcessConcept> --interactive # to generate all the boilerplate for an interactive SIB
cdb_cellmaps init <YourSibName> <ProcessConcept> --automated # to generate all the boilerplate for an automated SIB

# other flags, --python_version <X.Y> or --docker_image <image:tag> to specify the python version or docker image to use (one of these is required)
cdb_cellmaps init <YourSibName> <ProcessConcept> --interactive --python_version 3.8 # to generate all the boilerplate for an interactive SIB with python:3.8-slim
cdb_cellmaps init <YourSibName> <ProcessConcept> --automated --docker_image tensorflow/tensorflow:2.8.0 # to generate all the boilerplate for an automated SIB with a specific docker image
```

#### Eval

```bash
# to evaluate your sib, optional flag --tests to generate tests (not fully implemented yet)
# performs mypy static type checking
# it will also add a Label to the DockerFile, with the SIB model and other metadata (this is required by the Cinco De Bio platform)
cdb_cellmaps eval <path_to_main.py> 
cdb_cellmaps eval <path_to_main.py> --tests # to also generate tests (not fully implemented yet - but will generate the boilerplate at least)
```

### Directory Structure

Currently cincodebio only supports Docker images for running SIBs.
(Support for other runtimes (e.g. services with simpler dependencies) will be added in the future.)

The directory structure for the SIB should be as follows:

```plaintext
.
├── Dockerfile             # Docker configuration for building the service image
├── app/                   # Application source code
│   ├── __init__.py        # Initialize the app module
│   ├── main.py            # Entry point of the application
│   ├── *.py               # Any other Python modules you wish to include to implement your SIB
│   └── services/          # Folder for service-specific modules (if needed)
│       ├── __init__.py    # Initialize the services module
│       └── example.py     # Example service logic
    ├── templates/         # Folder for frontend templates (if interactive SIB)
│       ├── your-front-end-template.html.j2   # Jinja2 template(s) for the frontend (if interactive SIB)      
├── tests/
    └── scripts/          # Folder for test scripts
│       ├── __init__.py   # Initialize the services module
│       └── test1.py
│   └── data/          # Folder for test data (if needed)
│       ├── *          # data file(s) for testing
├── requirements.txt       # Python dependencies (this library is a required dependency!)
├── README.md              # Project documentation
```

### Example Python Code (Automated SIB)

```python
# Example usage
from dataclasses import  dataclass
from enum import Enum

from cdb_cellmaps.data import SemanticDataType, OtherSemanticDataType # Import Semantic Data Types
from cdb_cellmaps.process import Automated, SomeProcessConcept # Import Process Concept

# Define Input DataClass
@dataclass
class YourSibNameProcessInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            smt2: bool # must match the keys from Output DataClass
        data_flow: DataFlow
    @dataclass
    class Data:
        smt: SemanticDataType
    system_parameters: SystemParameters
    data: Data

# Define Output DataClass
@dataclass
class YourSibNameProcessOutput:
    # Define Control Enum
    class Control(str, Enum): 
        success = 'success'
    @dataclass
    class Data:
        smt2: SemanticDataType2
    data: Data
    # If there is no decision made in the Control set default to success
    control: Control = Control.success

# Define YourSibName Class

class YourSibName(SomeProcessConcept,Automated): # inherit from Automated and SomeProcessConcept
    _ROUTING_KEY = 'YourSibName' # this will be deprecated as we will use the class name

    def __init__(self) -> None:
        super().__init__()

    def deserialize_process_input(self,body) -> YourSibNameProcessInput:
        return data_utils.decode_dict(data_class=YourSibNameProcessInput,data=body)

        
    def process(self, prefix, input: YourSibNameProcessInput) -> YourSibNameProcessOutput:
        # This is where the main logic of the SIB goes.
        # For cleaner code, you can define helper functions as modules, import them and use them here.

        input.data.smt.read() # if it's a file
        
        # Semantic types which are Data Structures (e.g. Dict, List, Tuple),
        # function as the datastructure they represent
        # e.g. for k, v in input.data.smt.items() # for Dict
        # e.g. for i in input.data.smt # for List, etc..

        
        return YourSibNameProcessOutput(
            data=YourSibNameProcessOutput.Data(
                smt2=SemanticDataType2.write(
                    data=input.data.smt,
                    path=prefix, # path to write the file to 
                    file_name='smt2'
                ) # write only necessary if the output is a file
            )
        )

# Run the SIB
if __name__ == '__main__':
    YourSibName().run()

```

### Example Python Code (Interactive SIB)

```python
# from the Cellmaps SDK (but same princials apply for SIBs in cellmaps), just the data and service concepts will be different
from dataclasses import dataclass
from enum import Enum
from cdb_cellmaps.data import PNG, NuclearStain, RegionsOfInterest, TissueMicroArray
from cdb_cellmaps import data_utils
from cdb_cellmaps.process import DeArray, Interactive


# What comes from the execution environment (this will be the input for the SIB, the user will be modelling with)
@dataclass
class ManualDearrayTMAPrepareTemplateInput:
    @dataclass
    class SystemParameters:
        @dataclass
        class DataFlow:
            rois: bool
        data_flow: DataFlow
    @dataclass
    class Data:
        tissue_micro_array: TissueMicroArray
    @dataclass
    class WorkflowParameters:
        nuclear_stain: NuclearStain
    
    workflow_parameters: WorkflowParameters
    data: Data
    system_parameters: SystemParameters

# The HTML Front end (this is always the same)
@dataclass
class ManualDearrayTMAPrepareTemplateOutput:
    html: str

# What the user submits from the Interaction (i.e. the data model your front end will be generating and sending back to the SIB)
@dataclass
class ManualDearrayTMAProcessInput:
    @dataclass
    class WorkflowParameters:
        rois: RegionsOfInterest
        
    workflow_parameters: WorkflowParameters

# What is returned to the Execution Environment (this will be the output for the SIB, the user will be modelling with)
@dataclass
class ManualDearrayTMAProcessOutput:
    @dataclass
    class WorkflowParameters:
        rois: RegionsOfInterest

    class Control(str, Enum):
        success = 'success'

    # If there is no decision made in the Control set default to success
    workflow_parameters: WorkflowParameters
    control: Control = Control.success
    


class ManualDearrayTMA(DeArray,Interactive):
    _ROUTING_KEY = 'ManualDearrayTMA' # this will be deprecated as we will use the class name
    def __init__(self) -> None:
        super().__init__()

    # will be deprecated in favour of generics in future
    def deserialize_prepare_template_input(self, body) -> ManualDearrayTMAPrepareTemplateInput:
        return data_utils.decode_dict(data_class=ManualDearrayTMAPrepareTemplateInput,data=body)


    def prepare_template(self, prefix, submit_url, input: ManualDearrayTMAPrepareTemplateInput) -> ManualDearrayTMAPrepareTemplateOutput:
        # Load the Jinja2 template from the /templates folder
        template = self.env.get_template("de_array_manual.html") # whatever the name of the template is

        # Load Nuclear Stain Image - in this case it is an ome-tiff file which browser can't render
        nuclear_stain_img = input.data.tissue_micro_array[input.workflow_parameters.nuclear_stain].read()

        
        # Reduce the size of the raw image by 5x so it doesn't blow the browser and convert to PNG
        png = PNG.write(
            data = nuclear_stain_img.reduce(factor=5),
            prefix=prefix.add_level('browser-images'), # add_level is a helper function to create a new prefix with a new level (i.e. sub directory)
            file_name=input.workflow_parameters.nuclear_stain)
        
        # Render the template with the image and the submit URL (this is generated by the SDK)
        return ManualDearrayTMAPrepareTemplateOutput(
            html=template.render(
                nuclear_stain_static = png.get_external_url(),
                endpoint=submit_url,
            ))
    
    # will be deprecated in favour of generics in future
    def deserialize_process_input(self,body) -> ManualDearrayTMAProcessInput:
        return data_utils.decode_dict(data_class=ManualDearrayTMAProcessInput,data=body)

    def process(self, prefix, input: ManualDearrayTMAProcessInput) -> ManualDearrayTMAProcessOutput:
        # This is where the main logic of the SIB goes.
        # For cleaner code, you can define helper functions as modules, import them and use them here.

        # In this case we are just returning the ROIs, so it's a simple pass through
        return ManualDearrayTMAProcessOutput(
            workflow_parameters=ManualDearrayTMAProcessOutput.WorkflowParameters(
                rois=input.workflow_parameters.rois
            )
        )

# Run the SIB
if __name__ == '__main__':
    ManualDearrayTMA().run()

```

---

## Contributing

The Cinco De Bio team is excited to work with the community to develop new SIBs for the cellmaps domain specific workflow language on the Cinco de Bio Platform.

We welcome contributions! Please follow these steps:

1. Find a git repository of SIBs that is part of the cellmaps ontology.
2. Fork the repository.
3. Create a new branch (`git checkout -b feature-name`).
4. Make your changes.
5. Commit your changes (`git commit -m 'Add feature'`).
6. Push to your branch (`git push origin feature-name`).
7. Open a pull request.


If you have any questions, please reach out to us at `colm.brandon@ul.ie`
If you wish to contribute to the Cinco De Bio platform, please visit the [Cinco De Bio GitHub repository](https://github.com/colm-brandon-ul/cincodebio)
If you wish to contribute to the Cinco De Bio domain specific sdk generator (which generated this library), please visit the [Cinco De Bio SDK Generator GitHub repository](https://github.com/colm-brandon-ul/cdb-sdk-gen)

---

## License

This project is licensed under the apache-2.0.

---

## Author(s)


Colm Brandon

---

## Contact

Have questions? Reach out to us:
Email: `colm.brandon@ul.ie`

