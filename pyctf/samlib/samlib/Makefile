py = $(shell python -c 'import sysconfig; print(sysconfig.get_path("include"))')
CFLAGS = -O2 -fPIC -I. -I$(py)

SRC = $(shell ls *.c)
OBJ = $(SRC:.c=.o)

all: samlib.a

samlib.a: $(OBJ)
	$(AR) crs $@ $(OBJ)

clean:
	rm -f *~ *.o *.so *.a
