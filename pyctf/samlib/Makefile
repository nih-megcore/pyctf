include ../../config/Makefile.config

inst = $(LIBDIR)
bin = $(BINDIR)

INSTFILES = _samlib.so

CFLAGS = -O3 -fPIC

targ = $(INSTFILES)

all: $(targ)

test:
	$(MAKE) -C tests

install: $(targ)
	@mkdir -p $(inst)
	cp $(INSTFILES) $(inst)

_samlib.so: _samlib.c samlib/samlib.a
	env PYMODNAME=_samlib PYMODCFLAGS="-Isamlib -fopenmp" PYMODLIBS="samlib/samlib.a -lgsl -lgslcblas -lm -lgomp -lfftw3" $(MAKE) -f $(CONFDIR)/Makefile.pymod

samlib/samlib.a:
	$(MAKE) -C samlib

clean-x:
	rm -f *~ *.so *.o *.pyc \#*
	cd samlib; rm -f *~ *.a *.o *.pyc \#*
