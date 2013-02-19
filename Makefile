all: clean

clean:
	rm -Rf build
	find . -name "*.pyc" | xargs rm

start:
	python src/adapter.py  &> server.log &

run_test:
	mkdir -p build/test
	nosetests --with-xunit --quiet --nocapture --xunit-file=build/test/nosetests.xml tests/*.py

stop:
	ps aux | grep [a]dapter.py | awk '{print $$2}' | xargs kill

test: start run_test stop
