Using the package requires the anaconda python distribution (https://www.anaconda.com/download)

Here are the steps:

1. Create a new environment with conda environment

`conda create -n farsightOPConv python=3.6`

2. Activate the environment

`conda activate farsightOPConv`

3. Install SimpleITK

`conda install -c https://conda.anaconda.org/simpleitk SimpleITK`

4. Navigate into the downloaded repository

`cd \path\to\the\folder\FarsightOPConversionAndMetrics`

5. Install the package

`pip install ./`