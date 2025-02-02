#include "vga_graphics.h"
#include <SDL2/SDL.h>
#include <stdio.h>

static SDL_Window *window = NULL;
static SDL_Renderer *renderer = NULL;
static SDL_Texture *texture = NULL;

int initVGADisplay(VGADisplay *display) {
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        printf("SDL 초기화 실패: %s\n", SDL_GetError());
        return -1;
    }
    window = SDL_CreateWindow("Virtual VGA Display", SDL_WINDOWPOS_CENTERED,
                              SDL_WINDOWPOS_CENTERED, SCREEN_WIDTH, SCREEN_HEIGHT, 0);
    if (!window) {
        printf("윈도우 생성 실패: %s\n", SDL_GetError());
        return -1;
    }
    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (!renderer) {
        printf("렌더러 생성 실패: %s\n", SDL_GetError());
        return -1;
    }
    texture = SDL_CreateTexture(renderer, SDL_PIXELFORMAT_ARGB8888,
                                SDL_TEXTUREACCESS_STREAMING, SCREEN_WIDTH, SCREEN_HEIGHT);
    if (!texture) {
        printf("텍스처 생성 실패: %s\n", SDL_GetError());
        return -1;
    }
    for (int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        display->framebuffer[i] = 0xFF000000;
    }
    printf("VGA 디스플레이 초기화 완료\n");
    return 0;
}

void updateVGADisplay(VGADisplay *display) {
    SDL_UpdateTexture(texture, NULL, display->framebuffer, SCREEN_WIDTH * sizeof(uint32_t));
    SDL_RenderClear(renderer);
    SDL_RenderCopy(renderer, texture, NULL, NULL);
    SDL_RenderPresent(renderer);

    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        if (event.type == SDL_QUIT) {
            SDL_Quit();
        }
    }
}
