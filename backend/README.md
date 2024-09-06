# debuggingDragons

## Set up and how to run the app

1. Make sure python and vscode are installed.
2. Add Conda to the System PATH
   For Windows 10/11:

   1. Open Environment Variables:
      Right-click on the Start menu, select System.
      Click Advanced system settings > Environment Variables.
   2. Edit the PATH Variable:
      Under System variables (or User variables), find and select Path.
      Click Edit.
   3. Add the New Paths:
      Click New and add:
      C:\Users\${user}\anaconda3
      C:\Users\${user}\anaconda3\Scripts
      C:\Users\${user}\anaconda3\Library\bin

   ***

   For Linux/macOS:

   1. Open Terminal.
   2. Edit the Shell Profile:
      Use a text editor to open your shell profile file:
      Bash: nano ~/.bashrc
      Zsh: nano ~/.zshrc
   3. Add Conda to PATH:
      Add the following line:
      export PATH="$HOME/anaconda3/bin:$PATH"
   4. Apply Changes:
      Save and close the file.
      Run source ~/.bashrc or source ~/.zshrc.

3. Install the dependencies in `environment.yml` via one of these methods:
   - Clone the conda environment (probably better). Download conda/conda navigator, in conda navigator import `environment.yml`, launch vscode under 'Flask' environment. Or just create the conda environment in CLI using `conda env create -f environment.yml`, `conda activate Flask`
   - Just pip install the missing dependencies. `conda install pip` Important ones are flask and flask alchemy and anything you are missing when you run the app. `pip install flask flask-sqlalchemy`.
4. Launch vscode -> open folder -> this repo
5. In your terminal in VSC, navigate to this directory containing app.py. Run `python app.py`.
6. Open your browser, go to `http://localhost:5000/`.

## Google docs

https://docs.google.com/document/d/1m8FPXPHyh6ocvPlVjcdsX1Ma0YKQ7qh7JQH9lEzI2T8/edit
