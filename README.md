# Job Hunting App

This repository provides a small sample web application to help Japanese job seekers research companies.  
The backend downloads IR information from EDINET, extracts text from PDFs and asks OpenAI's GPT model to
summarise company strengths, challenges and example motivation statements. The frontend is a simple
React interface built with Vite.

The backend exposes two endpoints:

- `POST /search_company` に `{ "company_name": "トヨタ自動車" }`
- `POST /search_by_condition` に、業種・所在地・最低年収・社風などの条件を含む JSON ボディ

The steps below walk you through setting up the environment, running the application locally and building
for production. Commands assume Ubuntu&nbsp;22.04.

## Directory structure

project/
├── backend/
│ ├── main.py # FastAPI application
│ ├── requirements.txt # Python dependencies
│ ├── .env.example # template for your OpenAI API key
│ └── companies.json # sample company data for condition search
├── frontend/
│ ├── src/ # React source code
│ │ ├── App.jsx
│ │ ├── main.jsx
│ │ └── index.css
│ ├── public/
│ │ └── index.html
│ ├── package.json # Node dependencies
│ └── vite.config.js # Vite configuration

markdown
コピーする
編集する

## Prerequisites
- **Python 3.10** 以上
- **Node.js 18** 以上

## Environment setup
行頭が `$` の行はターミナルで実行してください。

1. **Clone this repository**
   ```bash
   $ git clone <this repository url>
   $ cd JOBhunting
Install Python and create a virtual environment

bash
コピーする
編集する
$ sudo apt update
$ sudo apt install -y python3 python3-venv python3-pip
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r project/backend/requirements.txt
(venv) $ cp project/backend/.env.example project/backend/.env
# open project/backend/.env and set your OpenAI API key
Install Node.js and frontend dependencies

bash
コピーする
編集する
$ curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
$ sudo apt install -y nodejs
$ cd project/frontend
$ npm install
Running the servers
Python 仮想環境を有効化したターミナルでバックエンドを起動します。

bash
コピーする
編集する
(venv) $ cd project/backend
(venv) $ uvicorn main:app --reload --host 0.0.0.0 --port 8000
別ターミナルでフロントエンド開発サーバを起動します。

bash
コピーする
編集する
$ cd project/frontend
$ npm run dev
両方起動したらブラウザで http://localhost:5173 を開いてください。
停止する場合は各ターミナルで Ctrl+C を押します。

Building for production
フロントエンドを静的ファイルとしてビルドする場合は次を実行します。

bash
コピーする
編集する
$ cd project/frontend
$ npm run build
生成物は project/frontend/dist/ に出力されます。ローカル確認は

bash
コピーする
編集する
$ npm run preview
バックエンドは --reload を外した Uvicorn もしくは他の ASGI サーバで常時稼働できます。

Notes
.env には OpenAI API キーが含まれるため 絶対にコミットしない でください。

companies.json は条件検索用のデモデータです。必要に応じて編集してください。

EDINET へのアクセスには安定したネットワークが必要です。書類が見つからない場合、API は 404 を返します。