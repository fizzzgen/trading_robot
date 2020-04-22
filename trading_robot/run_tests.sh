pip3 install pytest-xdist
python3 -m pytest -n 10 test/
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
