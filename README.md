# _SITCHENSIS_
python-based program to error check and calculate geometry of  3D tree crown-mapping data

### What is this repository for? ###

* This program will take 3D tree mapping data collected in the field and calculate whole-tree geometry. It will go through several steps along the way to first error check and visualize the data before actually calculating the final numbers. The data are imported from a single provided excel template for each tree. 

* Version: 0.0.1

### Where do I learn how to use it? ###

 * Click on the Wiki tab above to see a complete set of instructions for using _SITCHENSIS_

### How do I get set up? ###

* This package will run with a current installation of conda or miniconda and python>=3.X

* Configuration:
  * Install anaconda or miniconda
  * Open an anaconda command prompt
  * Create a new environment with the latest version of python  
    if you want to call your environment myEnv then:  
    `conda create -n myEnv python=3.6`  
    when prompted to download/update packages enter  
    `y`  
    if on a Mac you need a "framework build" of python, you can do this by running as an additional step:  
    `conda install python.app`  
    more information about this here:  
    <https://matplotlib.org/faq/osx_framework.html>

  * Activate the environment  
     In Windows:  
    `conda activate myEnv`  
     On Mac or Linux:  
     `source activate myEnv`
  * Install the package to the environment (this may take a while)   
   `pip install git+https://github.com/northcoastmountainrat/Sitchensis`
  * If this does not work because git is not installed either install git or clone the repository using the "Clone or downloan" button. Then navigate to the folder up just installed using:
  `cd pathtorepository/Sitchensis-maser`
  * Lastly, insure that the vpython module is installed by entering in the command prompt:
  `conda install -c vpython vpython`
  
* Test your installation one of two ways:
 1. Using Jupyter notebooks (must download repostory)
 > * In an Anaconda prompt with the environment activated that was just created enter:   
  `jupyter notebook` 
 > * Browse to the folder where you downloaded the repository to, open the "SitchensisTest" test folder and click on the "TreeMappingProgramExample.ipynb" file. 
 > * Run each chunk of code to see the program in operation. 
  
  2. Using the Anaconda command prompt with the new environment activated. 
 > * Download the data file in the "SitchensisTests" folder called "Mothership_Clean.xlsx"  
 > * Open an Anaconda command prompt  
   PC or Linux users enter:   
   `python run_tree.py`  
   Mac users enter:    
   `pythonw run_tree.py`
 > * Browse to the directory containing the "Mothership_Clean.xlsx" file and open it
 > * If configured properly a folder with outputs will be created called "SitchensisOutputs." In it will be two log files and a calculated output file with the date appended.   
 > * Windows of scatterplots should pop up for outlier scanning (currently disabled).
 > * Once the scatterplot windows are closed, a browser window will pop up and render a 3D tree from the excel file. 

* How to run the program
  * Use the provided excel template to enter data. Save data into any directory.
  * Open an anaconda command prompt and activate your environemnt as detailed above
  * Type `python run_tree.py` (PC or Linux) or `pythonw run_tree.py` (Mac)
  * Browse to the folder with the tree file in it and click open
  * Close the two scatterplot windows that appear after screening for errors (currently disabled).
  * Outputs are placed into new subfolder called "SitchensisOutputs"
  * Tree model is displayed in a browser window
  
* Dependencies: 
  * Python 3.x, xlrd, pandas 0.21.0 or greater, numpy, matplotlib, tkinter, sys, os, scipy, xlsxwriter, vpython, numbers, all .py files in the Sitchensis folder
  * Dependencies are automatically downloaded when the package is installed.
  * Dependencies can also be downloaded by creating an environment called 'sitchensis' with the included .yml file  
  `conda env create --file FullFilePath\sitchensis.yml`

### Who do I talk to? ###

* Repo owner or admin: Russell Kramer rdk10@uw.edu
* Other community or team contact
