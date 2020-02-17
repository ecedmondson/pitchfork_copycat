export PYTHONPATH=$PWD

echo "Input venv name (default is venv):"
read venvname
echo "Starting virtual env."

source "$venvname/bin/activate"
pip3 install -r requirements.txt

source venv/bin/activate
echo "Input DB hostname:"
read DBHOST
export HOST=$DBHOST

echo "Input DB username:"
read DBUSER
export USER=$DBUSER

echo "Input DB password:"
read DBPW
export PW=$DBPW

echo "Input DB name:"
read DBNAME
export DB=$DBNAME

python app.py
