# debuggingDragons

## Set up and how to run the app

1. Make sure python and vscode are installed.
2. Add Conda to the System PATH
   Follow these steps to add the necessary paths to your system's PATH environment variable:

For Windows 10/11:
Open Environment Variables:

Right-click on the Start menu and select System.
Click on Advanced system settings on the left side.
In the System Properties window, click on the Environment Variables button.
Edit the PATH Variable:

In the Environment Variables window, find the Path variable under System variables (or User variables if you only want to add it for your user account) and select it.
Click on Edit.
Add the New Paths:

In the Edit Environment Variable window, click New and add the following paths one by one:
C:\Users\${user}\anaconda3
C:\Users\${user}\anaconda3\Scripts
C:\Users\${user}\anaconda3\Library\bin

3. Install the dependencies in `environment.yml` via one of these methods:
   - Clone the conda environment (probably better). Download conda/conda navigator, in conda navigator import `environment.yml`, launch vscode under 'Flask' environment. Or just create the conda environment in CLI using `conda env create -f environment.yml`, `conda activate Flask`
   - Just pip install the missing dependencies. Important ones are flask and flask alchemy and anything you are missing when you run the app. `pip install flask flask-sqlalchemy`.
4. Launch vscode -> open folder -> this repo
5. In your terminal in VSC, navigate to this directory containing app.py. Run `python app.py`.
6. Open your browser, go to `http://localhost:5000/`.

## Google docs

https://docs.google.com/document/d/1m8FPXPHyh6ocvPlVjcdsX1Ma0YKQ7qh7JQH9lEzI2T8/edit
