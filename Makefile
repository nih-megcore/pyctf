include config/Makefile.config

# Use "make install" to install into the directories specified in config/Makefile.config.
# Use "make symlinks" to additionally create symbolic links in DESTBIN and DESTLIB.
# Use "make usersite" to add the LIBDIR dir to sys.path, so you don't need to set PYTHONPATH.

DESTBIN = $(HOME)/bin
DESTLIB = $(HOME)/lib

targets = pyctf parsemarks avghc StockwellDs thresholdDetect fiddist bids plothdm

all:
	for x in $(targets) ; do \
		$(MAKE) -C $$x $@ || exit ;\
	done

install: all
	for x in $(targets) ; do \
		$(MAKE) -C $$x $@ || exit ;\
	done

symlinks: install
	mkdir -p $(DESTBIN)
	mkdir -p $(DESTLIB)
	@for x in $(BINDIR)/*.py $(BINDIR)/parsemarks $(BINDIR)/matlab ; do \
		y=`basename $$x` ; \
		echo ln -s -f $$x $(DESTBIN)/$$y ; \
		ln -s -f $$x $(DESTBIN)/$$y ; \
	done
	ln -s -f $(LIBDIR) $(DESTLIB)

usersite: install
	for x in $(LIBDIR); do \
		d=`python -c "import site; print(site.USER_SITE)"`; \
		echo installing into $$d; \
		mkdir -p $$d; \
		dirname $(LIBDIR) > $$d/pyctf.pth; \
	done

clean: clean-x
