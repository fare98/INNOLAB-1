
# NASA Orion Asteroid Mapper

## Overview
This project is a web application that integrates data from NASA and the Orion context broker to display information about asteroids. The application fetches asteroid data from NASA and processes it through Orion, presenting it on a web-based map interface.

## Features
- Fetching and processing asteroid data from NASA.
- Integration with Orion context broker for data management.
- A web interface displaying asteroids on a map.

## Requirements
- Python 3.x
- Docker and Docker Compose
- Dependencies listed in `requirements.txt`.

## Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/fare98/INNOLAB-1.git]
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
3. Use Docker Compose to set up the Orion context broker and MongoDB:
   ```bash
   docker-compose up -d
   ```
   Make sure to run this command inside the `INNOLAB-1` directory.

## Usage
1. Start the server:
   - On Windows:
     ```bash
     cd src
     python.exe server.py
     ```
   - On Linux:
     ```bash
     cd src
     python3 server.py
     ```
2. Open `localhost:8000` in a web browser to view the NASA Asteroids Map.
