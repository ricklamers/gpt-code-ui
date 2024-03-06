# Changelog #

## March 06, 2024 ##
* Added this changelog to the documentation section
* Produced graphs and images are resizable now via a handle at their lower right corner

## March 04, 2024 ##
* Added support for [`py3dmol`](https://3dmol.csb.pitt.edu/doc/index.html) plots: Just upload a `.pdb`, `.xyz` `.sdf`, `.mol`, or `.cube` file and request a plot
* Rework of internal handling of different result types

## February 29, 2024 ##
* Added [`bio`](https://github.com/ialbert/bio) and [`docx`](https://pypi.org/project/docx/) to the list of preinstalled Python packages
* Added kernel control buttons to the sidebar
* Added command and button to interrupt code execution
* Visual cleanup of the sidebar
* More resilience against errors and failures in the internal infrastructure parts
* More consistently monitor last access to the individual kernels and clean up their resources and storage regularly

## February 26, 2024 ##
* Added a plugin system that allows system admins to provide additional, specialized functions to be called by the generated code

## February 17, 2024 ##
* Added notification if the app is open in more than one browser tab (which would have led to inconsistent result output).
* Extensive refactoring and simplification of the internal infrastructure
* Made special commands `clear` and `reset` case-insensitive.

## February 11, 2024 ##
* Switched to vector graphics output for plots. This enables support for non-Western typefaces and improves visuali quality of the plots.
* Added support for Antropic Claude language models in addition to OpenAI GPT

## January 18, 2024 ##
* Added [`XlsxWriter`](https://github.com/jmcnamara/XlsxWriter) to the list of preinstalled Python packages
* Added support for generating word clouds
* Added Disclaimer popup
* Added demo video

## November 09, 2023 ##
* Improve isolation of kernels to prevent potential cross-talk between user sessions

## October 24, 2023 ##
* Improved chat history sent to the LLM:
  * more consistent truncation to avoid running over the context length limit too quickly
  * include a sneak preview into uploaded files to allow for the LLM to produce better-suited code

## October 17, 2023 ##
* Allow navigating back to previous prompts with `Alt + Up/Down`
* Support downloading data assets from Palantir Foundry via the [`foundry-dev-tools`](https://github.com/emdgroup/foundry-dev-tools) library

## September 18, 2023 ##
* Removed option to set the API key in the frontend
* Added [`rdkit`](https://www.rdkit.org), [`scikit-learn`](https://scikit-learn.org/stable/), and [`scipy`](https://scipy.org) to the list of preinstalled Python packages
* Allowed (de)activating the automatic generation of commands to install missing packages

## August 04, 2023 ##
* Use one kernel per individual user's session
* Added support for `rdkit`-generated molecule structure plots (`png` iamges sent as `execute_result`)
* Several improvements for stability and resilience

## July 24, 2023
* Added support for markdown table output
* Add a sneak-peek into specific file types to allow for the LLM to generate more suitable code to deal with the file content
