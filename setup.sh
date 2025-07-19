#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers *with* dependencies (in user mode, no root)
playwright install --with-deps

# Download SpaCy model (optional)
python -m spacy download en_core_web_sm
