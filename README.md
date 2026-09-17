# Data Project Template

<a target="_blank" href="https://datalumina.com/">
    <img src="https://img.shields.io/badge/Datalumina-Project%20Template-2856f7" alt="Datalumina Project" />
</a>

## Cookiecutter Data Science
This project template is a simplified version of the [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org) template, created to suit the needs of Datalumina and made available as a GitHub template.

## Adjusting .gitignore

Ensure you adjust the `.gitignore` file according to your project needs. For example, since this is a template, the `/data/` folder is commented out and data will not be exlucded from source control:

```plaintext
# exclude data from source control by default
# /data/
```

Typically, you want to exclude this folder if it contains either sensitive data that you do not want to add to version control or large files.

## Duplicating the .env File
To set up your environment variables, you need to duplicate the `.env.example` file and rename it to `.env`. You can do this manually or using the following terminal command:

```bash
cp .env.example .env # Linux, macOS, Git Bash, WSL
copy .env.example .env # Windows Command Prompt
```

This command creates a copy of `.env.example` and names it `.env`, allowing you to configure your environment variables specific to your setup.


## Yahtzee Dice Game

A small, self-contained dice game lives in `src/yahtzee/`. Play it with:

```bash
python -m src.yahtzee                  # prompts for player names
python -m src.yahtzee Alice Bob        # two players
python -m src.yahtzee Solo --seed 42   # repeatable dice, handy for debugging
```

### Rules

Thirteen rounds. Each turn you roll five dice, then reroll any of them up to twice
more, keeping the dice you like between rolls. You then write the roll into one of
the thirteen categories — each can only be used once, so a bad roll sometimes means
taking a zero somewhere.

| Category | Scores |
| --- | --- |
| Ones … Sixes | Total of the dice showing that face |
| Three / Four of a Kind | Total of all five dice, if three (or four) match |
| Full House | 25, for three of one face and two of another |
| Small Straight | 30, for four consecutive faces |
| Large Straight | 40, for five consecutive faces |
| Yahtzee | 50, for five of a kind |
| Chance | Total of all five dice |

Score 63 or more across the upper section (Ones through Sixes) and you get a 35
point bonus. Highest total after thirteen rounds wins; ties are shared.

### Layout

```
src/yahtzee
├── dice.py       <- rolling, holding, and the three-roll limit
├── scoring.py    <- the thirteen categories and the score card
├── game.py       <- turns, rounds, and standings (no I/O)
└── cli.py        <- the terminal interface
```

Run the tests with `pytest tests`.


## Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── README.md          <- The top-level README for developers using this project
├── data
│   ├── external       <- Data from third party sources
│   ├── interim        <- Intermediate data that has been transformed
│   ├── processed      <- The final, canonical data sets for modeling
│   └── raw            <- The original, immutable data dump
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
└── src                         <- Source code for this project
    │
    ├── __init__.py             <- Makes src a Python module
    │
    ├── config.py               <- Store useful variables and configuration
    │
    ├── dataset.py              <- Scripts to download or generate data
    │
    ├── features.py             <- Code to create features for modeling
    │
    │    
    ├── modeling                
    │   ├── __init__.py 
    │   ├── predict.py          <- Code to run model inference with trained models          
    │   └── train.py            <- Code to train models
    │
    ├── plots.py                <- Code to create visualizations 
    │
    └── services                <- Service classes to connect with external platforms, tools, or APIs
        └── __init__.py 
```

--------