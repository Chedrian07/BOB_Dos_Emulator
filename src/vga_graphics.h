#ifndef VGA_GRAPHICS_H
#define VGA_GRAPHICS_H

#include <stdint.h>

#define SCREEN_WIDTH  640
#define SCREEN_HEIGHT 480

typedef struct {
uint32_t framebuffer[SCREEN_WIDTH * SCREEN_HEIGHT];
} VGADisplay;

int initVGADisplay(VGADisplay *display);
void updateVGADisplay(VGADisplay *display);

#endif  // VGA_GRAPHICS_H
