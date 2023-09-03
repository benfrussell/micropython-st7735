# micropython-st7735
Pure MicroPython module for driving ST7735 displays

Built with the goal of driving an ST7735 display optimized for a low memory footprint. The ST7735 object consumes ~4.5kB of RAM with the font cache and ~2kB without.

Tested using the [DFRobot 0.96" 160x80 Color SPI TFT Display](https://www.dfrobot.com/product-2445.html)

### Current Features
* Sending ST7735 commands & data
* Drawing rectangles
* Basic text drawing
* Fast text drawing using an ASCII character font cache
* Line drawing
* Ellipse drawing
* Polygon drawing
