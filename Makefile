TEST_COMMAND = nosetests --with-xunit --quiet --nocapture --nologcapture --xunit-file=build/test/nosetests.xml


all: clean


dependencies:
	rm -Rf dependencies
	mkdir dependencies
	git clone https://code.google.com/p/bfpy/ dependencies/bfpy
	sed -i.bak 's/https:\/\/api.betfair.com\/global\/v3\/BFGlobalService/http:\/\/localhost:8889\/BFGlobalService/g' dependencies/bfpy/src/bfpy/bfglobals.py
	sed -i.bak 's/https:\/\/api.betfair.com\/exchange\/v5\/BFExchangeService/http:\/\/localhost:8889\/BFExchangeService/g' dependencies/bfpy/src/bfpy/bfglobals.py
	
	#ZSI-2.1_a1
	#sudo patch /usr/local/lib/python2.7/dist-packages/ZSI/writer.py patches/ZSI.writer.patch
	#sudo patch /usr/local/lib/python2.7/dist-packages/ZSI/wstools/c14n.py patches/ZSI.wstools.c14n.patch


clean:
	rm -Rf build
	find . -name "*.pyc" | xargs rm


start:
	python src/smkadapter/adapter.py  &> server.log &


stop:
	ps aux | grep [a]dapter.py | awk '{print $$2}' | xargs kill


create_test_dir:
	mkdir -p build/test


unit_tests: create_test_dir
	$(TEST_COMMAND) tests/*_test.py

integration_tests: create_test_dir
	$(TEST_COMMAND) tests/*integration_tests.py

acceptance_tests_suit: create_test_dir
	$(TEST_COMMAND) tests/acceptance_tests.py

acceptance_tests: start acceptance_tests_suit stop

test: unit_tests integration_tests acceptance_tests

try:
	python src/smkadapter/investigation.py ${action}


external_client_test: dependencies
	$(TEST_COMMAND) tests/bfpybot.py