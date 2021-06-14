include ../config/Makefile.config

targets = samiir st sensortopo param roi datamanager samlib
ttargets = samlib

all:
	for x in $(targets) ; do \
		$(MAKE) -C $$x $@ || exit ;\
	done

test:
	for x in $(ttargets) ; do \
		$(MAKE) -C $$x $@ || exit ;\
	done

install: all
	for x in $(targets) ; do \
		$(MAKE) -C $$x $@ || exit ;\
	done
	cp *.py $(LIBDIR)

clean: clean-x
