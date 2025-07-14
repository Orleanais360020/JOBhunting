# Job Hunting App

This repository provides a web application to help Japanese job seekers research companies.
The backend downloads IR information from EDINET, extracts text from PDFs and asks OpenAI's GPT model to
summarise company strengths, challenges and example motivation statements. The frontend is a simple
React interface built with Vite.

The backend exposes two endpoints. The company search uses fuzzy matching on
EDINET so that similar corporate names can still return results. The condition
search downloads the EDINET corporate list and filters by industry code and
prefecture:

- `POST /search_company` with `{ "company_name": "トヨタ自動車" }`
- `POST /search_by_condition` with `{ "industry_code": "5200", "prefecture": "東京" }`

The steps below walk you through setting up the environment, running the application locally and building
for production. Commands assume Ubuntu 22.04.

## Directory structure

```
project/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # template for your OpenAI API key
├── frontend/
│   ├── src/                 # React source code
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
```

## Prerequisites
- **Python 3.10** or later
- **Node.js 18** or later

## Environment setup
The commands below install the required tools and libraries. Lines starting with `$` are executed in the terminal.

1. **Clone this repository**
   ```bash
   $ git clone <this repository url>
   $ cd JOBhunting
   ```
2. **Install Python and create a virtual environment**
   ```bash
   $ sudo apt update
   $ sudo apt install -y python3 python3-venv python3-pip
   $ python3 -m venv venv
   $ source venv/bin/activate
   (venv) $ pip install -r project/backend/requirements.txt
   (venv) $ cp project/backend/.env.example project/backend/.env
   # open project/backend/.env and set your OpenAI API key
   ```
3. **Install Node.js and frontend dependencies**
   ```bash
   $ curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   $ sudo apt install -y nodejs
   $ cd project/frontend
   $ npm install
   ```

## Running the servers
With the Python virtual environment activated in one terminal, start the FastAPI backend:
```bash
(venv) $ cd project/backend
(venv) $ uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Leave that running. In a separate terminal start the React development server:
```bash
$ cd project/frontend
$ npm run dev
```
After both servers start, open your browser to **http://localhost:5173** to try the app.

To stop either server, return to its terminal and press `Ctrl+C`.

## Building for production
When you want to publish the frontend as static files, run:
```bash
$ cd project/frontend
$ npm run build
```
The built files will be placed in `project/frontend/dist/`. You can preview them locally with:
```bash
$ npm run preview
```
The backend can be served in production using Uvicorn without `--reload` or via another ASGI server.

## Notes
- Do **not** commit your `.env` file. It contains your private OpenAI API key.
- Access to EDINET may require a stable network connection. The search endpoint uses fuzzy matching but will still return a `404` error when nothing similar is found.
