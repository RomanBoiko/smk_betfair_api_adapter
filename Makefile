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


unit_tests: create_test_dir
	$(TEST_COMMAND) tests/*_test.py

integration_tests: create_test_dir
	$(TEST_COMMAND) tests/integration_tests.py

acceptance_tests_suit: create_test_dir
	$(TEST_COMMAND) tests/acceptance_tests.py

acceptance_tests: start acceptance_tests_suit stop

test: unit_tests integration_tests acceptance_tests
