#############################################
OSC Transformer Based Extractor
#############################################

|osc-climate-project| |osc-climate-slack| |osc-climate-github| |pypi| |build-status| |pdm| |PyScaffold|

***********************************
OS-Climate Data Extraction Tool
***********************************

This project provides a CLI tool and Python scripts to train Transformer models (via Hugging Face) for two primary tasks:  
1. **Relevance Detection**: Determines if a question-context pair is relevant.  
2. **KPI Detection**: Fine-tunes models to extract key performance indicators (KPIs) from datasets like annual reports and perform inference.

Quick Start
^^^^^^^^^^^^^

To install the tool, use pip:

.. code-block:: shell

    $ pip install osc-transformer-based-extractor

After installation, you can access the CLI tool with:

.. code-block:: shell

    $ osc-transformer-based-extractor

This command will show the available commands and help via Typer, our CLI library.

Commands and Workflow
^^^^^^^^^^^^^^^^^^^^^^^

1. Relevance Detection
--------------------------

**Fine-tuning the Model:**

Assume your project structure looks like this:

.. code-block:: text

    project/
    │
    ├── kpi_mapping.csv
    ├── training_data.csv
    ├── data/              
    │   └── (JSON files for inference)
    ├── model/             
    │   └── (Model-related files)
    ├── saved__model/      
    │   └── (Output from training)
    ├── output/            
    │   └── (Results from inference)

Use the following command to fine-tune the model:

.. code-block:: shell

    $ osc-transformer-based-extractor relevance-detector fine-tune \
      --data_path "project/training_data.csv" \
      --model_name "bert-base-uncased" \
      --num_labels 2 \
      --max_length 128 \
      --epochs 3 \
      --batch_size 16 \
      --output_dir "project/saved__model/" \
      --save_steps 500

**Running Inference:**

.. code-block:: shell

    $ osc-transformer-based-extractor relevance-detector perform-inference \
      --folder_path "project/data/" \
      --kpi_mapping_path "project/kpi_mapping.csv" \
      --output_path "project/output/" \
      --model_path "project/model/" \
      --tokenizer_path "project/model/" \
      --threshold 0.5

2. KPI Detection
---------------------

The KPI detection functionality includes **fine-tuning** and **inference**.

**Fine-tuning the KPI Model:**

Assume your project structure looks like this:

.. code-block:: text

    project/
    │
    ├── kpi_mapping.csv              
    ├── training_data.csv             
    │
    ├── model/                        
    │   └── (model-related files, e.g., tokenizer, config, checkpoints)
    │
    ├── saved__model/                 
    │   └── (Folder to store output from fine-tuning)
    │
    ├── output/                     
    │   └── (output files, e.g., inference_results.xlsx)


.. code-block:: shell

    $ osc-transformer-based-extractor kpi-detection fine-tune \
        --data_path "project/training_data.csv" \
        --model_name "bert-base-uncased" \
        --max_length 128 \
        --epochs 3 \
        --batch_size 16 \
        --learning_rate 5e-5 \
        --output_dir "project/saved__model/" \
        --save_steps 500


**Performing Inference:**

.. code-block:: shell

    $ osc-transformer-based-extractor kpi-detection inference \
        --data_file_path "project/data/input_dataset.csv" \
        --output_path "project/output/inference_results.xlsx" \
        --model_path "project/model/"


Training Data Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Relevance Detection Training File:

The training file should have the following columns:
- ``Question``
- ``Context``
- ``Label``

Example:

.. list-table:: Training Data Example
   :header-rows: 1

   * - Question
     - Context
     - Label
   * - What is the company name?
     - The Company is exposed to a risk...
     - 0

2. KPI Detection Training File:

For KPI detection, the dataset should have these additional columns:

.. list-table:: KPI Detection Training Example
   :header-rows: 1

   * - Question
     - Context
     - Label
     - Company
     - Source File
     - KPI ID
     - Year
     - Answer
     - Data Type
   * - What is the company name?
     - ...
     - 0
     - NOVATEK
     - 04_NOVATEK_AR_2016_ENG_11.pdf
     - 0
     - 2016
     - PAO NOVATEK
     - TEXT

3. KPI Mapping File:

.. list-table:: KPI Mapping File Example
   :header-rows: 1

   * - kpi_id
     - question
     - sectors
     - add_year
     - kpi_category
   * - 1
     - In which year was the annual report...
     - OG, CM, CU
     - FALSE
     - TEXT

Developer Notes
^^^^^^^^^^^^^^^^^

Local Development
----------------------

Clone the repository:

.. code-block:: shell

    $ git clone https://github.com/os-climate/osc-transformer-based-extractor/

We use **pdm** for package management and **tox** for testing.

1. Install ``pdm``:

   .. code-block:: shell

      $ pip install pdm

2. Sync dependencies:

   .. code-block:: shell

      $ pdm sync

3. Add new packages (e.g., numpy):

   .. code-block:: shell

      $ pdm add numpy

4. Run ``tox`` for linting and testing:

   .. code-block:: shell

      $ pip install tox
      $ tox -e lint
      $ tox -e test

Contributing
^^^^^^^^^^^^^^

We welcome contributions! Please fork the repository and submit a pull request.  
Ensure you sign off each commit with the **Developer Certificate of Origin (DCO)**.  
Read more: http://developercertificate.org/.

Governance Transition
^^^^^^^^^^^^^^^^^^^^^^^^

On June 26, 2024, the **Linux Foundation** announced the merger of **FINOS** with OS-Climate.  
Projects are now transitioning to the [FINOS governance framework](https://community.finos.org/docs/governance).

Shields
^^^^^^^^^

|osc-climate-project| |osc-climate-slack| |osc-climate-github| |pypi| |build-status| |pdm| |PyScaffold|

.. |osc-climate-project| image:: https://img.shields.io/badge/OS-Climate-blue
   :alt: An OS-Climate Project
   :target: https://os-climate.org/

.. |osc-climate-slack| image:: https://img.shields.io/badge/slack-osclimate-brightgreen.svg?logo=slack
   :alt: Join OS-Climate on Slack
   :target: https://os-climate.slack.com

.. |osc-climate-github| image:: https://img.shields.io/badge/GitHub-100000?logo=github&logoColor=white
   :alt: Source code on GitHub
   :target: https://github.com/ModeSevenIndustrialSolutions/osc-data-extractor

.. |pypi| image:: https://img.shields.io/pypi/v/osc-data-extractor.svg
   :alt: PyPI package
   :target: https://pypi.org/project/osc-data-extractor/

.. |build-status| image:: https://api.cirrus-ci.com/github/os-climate/osc-data-extractor.svg?branch=main
   :alt: Build Status
   :target: https://cirrus-ci.com/github/os-climate/osc-data-extractor

.. |pdm| image:: https://img.shields.io/badge/PDM-Project-purple
   :alt: Built using PDM
   :target: https://pdm-project.org/latest/

.. |PyScaffold| image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
   :alt: Project generated with PyScaffold
   :target: https://pyscaffold.org/
