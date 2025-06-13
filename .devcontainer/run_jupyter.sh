#!/bin/sh
jupyter notebook \
    --notebook-dir='/notebooks' \
    --ip='*' --port=8888 \
    --NotebookApp.token="" \
    --no-browser --allow-root