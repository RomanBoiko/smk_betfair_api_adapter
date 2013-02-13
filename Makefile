all: clean

clean:
	find . -name "*.pyc" | xargs rm
	rm -R build

start:
	python src/betfair_soap_api_server.py  &> server.log &

run_test:
	mkdir -p build/test
	nosetests --with-xunit --quiet --xunit-file=build/test/nosetests.xml tests/*.py

stop:
	ps aux | grep [b]etfair_soap_api_server | awk '{print $$2}' | xargs kill

test: start run_test stop
