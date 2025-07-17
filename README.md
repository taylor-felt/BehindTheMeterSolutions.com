# BehindTheMeterSolutions.com

This project implements a small rate schedule configuration system. It uses a Flask backend with a SQLite database and a simple HTML/JavaScript front end.

## Running the application

Install dependencies and populate the database with the provided list of utilities:

```bash
pip install -r requirements.txt
python load_utilities.py  # one time to create states/utilities
python app.py
```

Open `index.html` in your browser. The page will communicate with the running Flask API on port `5000`.

## Features

* Import rate schedules from an Excel file.
* Dependent drop downs for state, utility and available rate schedules.
* Ability to view and update a selected schedule.
* Downloadable Excel template for importing data.
