# BehindTheMeterSolutions.com

This project implements a small rate schedule configuration system. It uses a Flask backend with a SQLite database and a simple HTML/JavaScript front end.

## Running the application

Install dependencies and populate the database with the provided list of utilities:

```bash
pip install -r requirements.txt
python load_utilities.py  # one time to create states/utilities
python app.py
```

Start the server and then visit `http://localhost:5000/` in your browser. The index page is served directly from Flask so the JavaScript can communicate with the API without CORS issues.

## Features

* Import rate schedules from an Excel file. The upload endpoint automatically skips the first two rows of the provided PG&E spreadsheet.
* Dependent drop downs for state, utility and available rate schedules.
* Ability to view and update a selected schedule.
* Downloadable Excel template for importing data.

## Node.js Real-Time Dashboard (Preview)

A prototype Node.js server has been added for experimenting with real-time
connections to an eGauge energy monitor. It serves files from `public/` and
broadcasts power data over WebSockets.

### Running

```bash
npm install
cp .env.example .env    # fill in your eGauge credentials
npm start
```

Then open `http://localhost:3000/` to view the dashboard.
