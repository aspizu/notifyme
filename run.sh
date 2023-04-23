#!/bin/bash
set -e

uvicorn server:application --reload --port 5000
