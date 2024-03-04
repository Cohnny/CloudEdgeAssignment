# Cloud Edge Assignment - Flask App

Cohnny Flobrandt

Ivan Kokalovic

Magnus Petersson

## Brief description of the project.

Movie database project using python and flask.

Users can register an account and add their favourite movies to the community driven SQL database.

## Features
* Login page
  * Username
  * Password

* Register page
  * Username
  * Password

* Secured password
  * Hashed

* Add your own movies
  * Title
  * Rating (1-100)
  * Description

* Remove you own movies

* List all user added movies
  * Title
  * Rating
  * Username

## Installation 

1. Clone repository

Clone link: https://github.com/Cohnny/CloudEdgeAssignment.git

2. Installation

Dockerfile is configured to automatically install requirements and dependencies.

3. Usage

Run main.py or open terminal and type: docker-compose up --build -d

## Configuration 

1. Default configuration 

Uses local sqlite3 database file.
Exposes port 5000

2. Advanced configuration

Can be configured to use azure sql database (see commented code line 18-36)

## Contribution 

1. This is a closed project. 

## Authors and acknowledgment 

Jimmy Berlin for inspiration and frustration.  

## Licenses

No license.

## Project status

Completed. 