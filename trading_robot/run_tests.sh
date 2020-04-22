apt-get install python3-pip
pip3 install pylint
pip3 install -r ../requirements.txt
pip3 install pytest-xdist
python3 -m pytest -n 10 test/
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm \.*
mkdir ~/.pylint/
echo "pylint..."
pylint *.py > ~/.pylint/test.log
pylint */*.py >> ~/.pylint/test.log
pylint */*/*.py >> ~/.pylint/test.log
echo 'pylint log: ~/.pylint/test.log'
echo 'total errors file length:'
wc -l ~/.pylint/test.log
