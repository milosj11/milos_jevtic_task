## Single script for collecting publication and actualites from [Troinex](https://troinex.ch/actualites/), [Communa de plan-les-ouates](https://www.plan-les-ouates.ch/actualites) and [République et canton de Genève](https://www.ge.ch/publication) web sites. 
The solution represents [a single script file](main.py) written in [Python 3](https://www.python.org/downloads/) and script ensures that the following steps are performed:
* Calls `collect_the_data` generic function with valid key word arguments 
* Function scrapes the data and stores them in the lists
* Converts collected data from lists into a JSON or CSV format 
* Creates `results` folder and saves file with proper extension as a final result

### First steps

* Clone this project to your local workspace - `git clone https://github.com/milosj11/milos_jevtic_task.git`
* Open the cloned project with you favorite IDE (e.g. _PyCharm_)
* Install required dependencies - `pip install -r requirements.txt` (optional: use a separate virtual environment)

### Running the script 

Script can be executed in two ways:
1. Without additional parameters - script creates three JSON files (separate file for each website)
2. With additional parameters - script should be run through use of command line arguments and params that can be provided are:
* `--site` refers to web site domain (`troinex`, `plan_les_ouates`, `ge`) from which the data will be collected. If not provided script will collect data from all three websites.
* `--format` refers to file type for the output (`csv` or `json`). Default file type is `json` as well. 
E.g.
```
1. python main.py --site troinex 
2. python main.py --site torinex --type csv 
3. python main.py --type csv 
```

***NOTE***: In order to make the script as generic as possible (and shorther) in some cases and in some parts we perform operations that is not necessary (e.g. Looping through the list with just one element; strip string which has no white space at begining or at the end).
