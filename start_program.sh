#!/bin/bash

docker compose stop && docker compose down
docker compose build
docker compose up
