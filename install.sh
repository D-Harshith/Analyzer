#!/bin/bash
playwright install --with-deps
python -m spacy download en_core_web_sm
