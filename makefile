install:
	pip3 install --upgrade pip &&\
		pip3 install -r requirements.txt

format:
	black -t py39 ./
	
run:
	python3 main.py

frun: format run

all: install format run
