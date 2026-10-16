#include <SFML/Graphics.hpp>
#include <SFML/Audio.hpp>
#include <iostream>
#include <fstream>
#include <vector>

constexpr int WIDTH = 128;
constexpr int HEIGHT = 64;
constexpr int SCALE = 6;
constexpr int FRAME_SIZE = (WIDTH * HEIGHT) / 8;
constexpr int NUM_FRAMES = 372;
constexpr float FRAME_TIME = 0.070f;

int main() {
    sf::RenderWindow window(sf::VideoMode(WIDTH * SCALE, HEIGHT * SCALE), "TELL ME WHY - Duong Domic [SFML Equalizer Player]");
    window.setFramerateLimit(60);

    // Doc frame tu tellmewhy_frames.bin
    std::ifstream binFile("tellmewhy_frames.bin", std::ios::binary);
    if (!binFile) {
        std::cerr << "Khong the mo file tellmewhy_frames.bin!" << std::endl;
        return -1;
    }
    std::vector<uint8_t> allFrames(NUM_FRAMES * FRAME_SIZE);
    binFile.read(reinterpret_cast<char*>(allFrames.data()), allFrames.size());
    binFile.close();

    sf::Music music;
    if (music.openFromFile("tellmewhy.mp3")) {
        music.setLoop(true);
        music.play();
    }

    sf::Texture texture;
    texture.create(WIDTH, HEIGHT);
    sf::Sprite sprite(texture);
    sprite.setScale(SCALE, SCALE);

    sf::Clock clock;
    std::vector<sf::Uint8> pixels(WIDTH * HEIGHT * 4, 255);

    while (window.isOpen()) {
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed || 
               (event.type == sf::Event::KeyPressed && event.key.code == sf::Keyboard::Escape))
                window.close();
            if (event.type == sf::Event::KeyPressed && event.key.code == sf::Keyboard::Space) {
                if (music.getStatus() == sf::Music::Playing) music.pause();
                else music.play();
            }
        }

        float t = music.getStatus() == sf::Music::Playing ? music.getPlayingOffset().asSeconds() : clock.getElapsedTime().asSeconds();
        int frameIdx = static_cast<int>(t / FRAME_TIME) % NUM_FRAMES;
        const uint8_t* frameData = &allFrames[frameIdx * FRAME_SIZE];

        for (int y = 0; y < HEIGHT; ++y) {
            for (int x = 0; x < WIDTH; ++x) {
                int byteIdx = y * 16 + (x / 8);
                int bitIdx = 7 - (x % 8);
                bool isWhite = (frameData[byteIdx] >> bitIdx) & 1;
                sf::Uint8 color = isWhite ? 255 : 0;
                int pIdx = (y * WIDTH + x) * 4;
                pixels[pIdx] = color;
                pixels[pIdx + 1] = color;
                pixels[pIdx + 2] = color;
                pixels[pIdx + 3] = 255;
            }
        }

        texture.update(pixels.data());
        window.clear();
        window.draw(sprite);
        window.display();
    }
    return 0;
}
