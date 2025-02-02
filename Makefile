CC = gcc
UNAME_S := $(shell uname -s)

INCFLAGS = -I./src `sdl2-config --cflags`
ifeq ($(UNAME_S),Darwin)
    INCFLAGS += -I/opt/homebrew/include
endif

CFLAGS = -Wall -Wextra -std=c99 $(INCFLAGS)
LIBS = `sdl2-config --libs`

SRCS = \
    src/main.c \
    src/bios.c \
    src/cpu.c \
    src/debugger.c \
    src/dma_controller.c \
    src/eisa_bus.c \
    src/interrupt_controller.c \
    src/timer.c \
    src/vga_graphics.c \
    src/virtual_storage.c

OBJS = $(SRCS:.c=.o)
TARGET = dos_sandbox

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(OBJS) -o $(TARGET) $(LIBS)

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean