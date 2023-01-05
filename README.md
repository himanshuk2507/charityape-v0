# Skraggle Fundraiser

## Prerequisites

`The following software is required for successfully running the server`

```
- Python >=3.6.0 (latest: 3.10.0)
- Redis Server
- PostgreSql Database
```

<!-- GETTING STARTED -->

## Getting Started

### Environment variables

Request a .env file for the project.

## 1. Installation

1. `Install Python, Redis and PostgreSQL`

    - Install Python: [https://python.org/download](https://python.org/download)
    - Install Redis: [https://redis.io/download](https://redis.io/download)
        - If on MacOS, you can also install Redis using Homebrew with `brew install redis`
    - Install PostgreSQL [https://www.postgresql.org/download/](https://www.postgresql.org/download/)
        - If on MacOS, you can also install PostgreSQL using Homebrew with `brew install postgres`

2. `Clone the repo`

```
git clone https://git.biggorilla.tech/bga/skraggle.git

cd skraggle/new_skraggle
```

## 2. Create and start a virtual environment

`Check whether virtualenv is already installed globally`

```
which virtualenv
```

`If it isn't, install`

```
pip3 install virtualenv
```

`Create a new virtual environment`

```
virtualenv .venv
```

`Start the virtualenv On Linux/MacOS computers:`

```
source .venv/bin/activate
```

`On Windows computers:`

```
\.venv\Scripts\activate
```

### Install required Packages and libs

```
pip3 install -r requirements.txt
```

### Set up environment variables

`Move the .env file you were given to the current folder`

```

mv /path/to/env/file/in/downloads/folder .

```

## 3. Migrate models

```

flask db upgrade

```

`and ensure migrations were completed successfully.`

## Run server

```

flask run

```

`App automatically listens on port 5000`
