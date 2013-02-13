all: clean

clean:
	find . -name "*.pyc" | xargs rm
	rm -R build

test:
	mkdir -p build/test
	nosetests --with-xunit --quiet --xunit-file=build/test/nosetests.xml tests/*.py

run:
	python src/betfair_soap_api_server.py
