# KageAgent
IRC bot written in Python.

## Features
- Task management
- SQLite database
- Task reminders
- IRC bot

## Commands

```text
!add DATA HORA TAREFA
!agenda
!done ID
!edit ID HORA TAREFA
!delete ID
!help
```

## Setup

```bash
git clone <repository-url>
cd kage-agent

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file based on `.env.example`.

## Run

```bash
python3 main.py
```
