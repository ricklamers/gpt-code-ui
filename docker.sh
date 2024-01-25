#!/bin/bash
sudo docker-compose -f docker-compose.yml down && sudo docker-compose -f docker-compose.yml up -d --build --no-deps --force-recreate
