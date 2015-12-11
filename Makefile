#!/usr/bin/make -f

SRCDIR=src

test:
	nosetests --with-doctest --verbosity=3 --detailed-errors --with-coverage --cover-erase --doctest-options='+ELLIPSIS' -exe -w src/usr/share/mirthless/lib

all: 
# Add commands here to build code.

install: test
	find ${SRCDIR} -type f | while read file ; do  \
			echo $$file ;\
			install -v -m 755 -o root -g root -d "$$(dirname "$(DESTDIR)/$$file")"; \
			if [ -x "$$file" ]; then \
				install -v -m 755 -o root -g root "$$file" "$(DESTDIR)/$$file"; \
			else \
				install -v -m 644 -o root -g root "$$file" "$(DESTDIR)/$$file"; \
			fi; \
	done

# Add commands here to set special permissions, owners, and groups.
# Example:
#
#	chmod u+s $(DESTDIR)/usr/bin/sudo

clean:
	debclean		
deb:
	debuild -uc -us -b
	
debclean:
	debuild clean
