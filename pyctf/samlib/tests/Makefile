TESTS = $(shell ls test_*.py)

all:
	for x in $(TESTS) ; do \
		PYTHONPATH=".." python ../runtests.py $$x ;\
	done
