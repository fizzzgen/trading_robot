apt-get install python3-pip
pip3 install -r ../requirements.txt
pip3 install pytest-xdist
python3 -m pytest -n 10 test/
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
