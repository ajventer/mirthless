#!/usr/bin/make -f

SRCDIR=src

test:
	nosetests  -x --with-doctest --verbosity=3 --detailed-errors --with-coverage --cover-erase --doctest-options='+ELLIPSIS' -exe -w src/lib

all: 
# Add commands here to build code.

install: test
	mkdir -p /home/$(USER)/.mirthless
	mkdir -p $(DESTDIR)/usr/share/mirthless
	cp -rfv ${SRCDIR}/*  $(DESTDIR)/usr/share/mirthless
	chmod -R 755 $(DESTDIR)/usr/share/mirthless
	chown -R root:root $(DESTDIR)/usr/share/mirthless
	cp -rfv etc $(DESTDIR)/
	chmod -R 755 $(DESTDIR)/etc
	chown -R root:root $(DESTDIR)/etc
	mkdir -p $(DESTDIR)/usr/games
	cp -f mirthless $(DESTDIR)/usr/games/
	chmod -R 755 $(DESTDIR)/usr/games
	chown root:root $(DESTDIR)/usr/games

clean:
	debclean		
deb:
	debuild -uc -us -b
	
debclean:
	debuild clean
