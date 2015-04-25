<h1>Installation</h1>

<h3>Run</h3>

virtualenv

<h3>Database</h3>

SQLAlchemy

<h3>Web Scraping</h3>

BeautifulSoup4
requests

<h3>Data Analysis</h3>

First, run:
```
sudo apt-get install gcc gfortran python-dev libblas-dev liblapack-dev cython
```

numpy
nose

Before continuing, run:
```
sudo apt-get install libjpeg8-dev libfreetype6-dev libpng12-dev
```

matplotlib
scipy
scikit-learn

<h1>Usage</h1>

Run the parser in the folder /battle_parser
This gets the JSON file containing all of the battle information: battleData.txt

The rest is automated:
```
python pkmn_matchup.py battle_parser/battleData.txt
```

<h1>Output</h1>

Runs 5 rounds of the clustering analysis using spectral clustering and stores results in a series of text files of the form
```
testi_results.txt
```
...where i is the test number