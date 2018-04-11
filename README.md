# Sitchensis
python-based program to error check and calculate geometry of  3D tree crown-mapping data

### What is this repository for? ###

* This program will take 3D tree mapping data collected in the field and calculate whole-tree geometry. It will go through several steps
* along the way to first error check and visualize the data before actually calculating the final numbers. The data are imported from a 
* single provided excel template for each tree. 

* Version: 0.0.1

### How do I get set up? ###

* This package will run with a current installation of conda or miniconda and python>=3.6

* Configuration: For the initial configuration
  * Install anaconda or miniconda
  * Open an anaconda command prompt
  * Create a new environment with the latest version of python: Ex: if you want to call your environment myEnv then  
    `conda create -n myEnv python=3.6`
  * Activate the environment  
    `activate myEnv`
  * Install the package to the environment  
   `pip install git+https://github.com/northcoastmountainrat/Sitchensis`

* How to run the program
  * Use the provided excel template to enter data. Save data into any directory.
  * Open an anaconda command prompt and activate your environemnt as detailed above
  * Type run_tree and enter
  * Browse to the folder with the tree file in it and click open
  * Close the two scatterplot windows that appear after screening for errors
  * Outputs are placed into new subfolder called "Sitchensis outputs"
  * Tree model is displayed in a browser window
  
* Dependencies: 
 - Python 3.x, xlrd, pandas 0.21.0 or greater, numpy, matplotlib, tkinter, sys, os, scipy, xlsxwriter, vpython, numbers, all .py files in the Sitchensis folder
 - Dependencies are automatically downloaded when the package is installed.

* Database configuration: I don't know what this means yet

* How to run tests: To test that the code is configured properly and working upload the clean data file in the "Sitchensis_tests" folder called "Mothership.xlsx." Run the MainBodyScript.py and navigate to this file. If configured properly a folder with outputs will be created called "SitchensisOutputs." In it will be two log files. Windows of scatterplots should pop up for outlier scanning. Once these are closed, a browser window will pop up and render a 3D tree from the excel file. 

* Deployment instructions: I don't know what this means. 

### Contribution guidelines ###

* Writing tests: ????
* Code review: ?????
* Other guidelines: ????

### Who do I talk to? ###

* Repo owner or admin: Russell Kramer rdk10@uw.edu
* Other community or team contact
