TEST_COMMAND = nosetests --with-xunit --quiet --nocapture --nologcapture --xunit-file=build/test/nosetests.xml


all: clean


clean:
	rm -Rf build
	find . -name "*.pyc" | xargs rm


start:
	python src/adapter.py  &> server.log &


stop:
	ps aux | grep [a]dapter.py | awk '{print $$2}' | xargs kill


create_test_dir:
	mkdir -p build/test


all_tests: create_test_dir
	$(TEST_COMMAND) tests/*.py


integration_tests: create_test_dir
	$(TEST_COMMAND) tests/smk_api_test.py


test: start all_tests stop
