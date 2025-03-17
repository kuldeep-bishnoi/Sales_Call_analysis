#!/bin/bash
# Script to download and install whisper.cpp

set -e  # Exit on error

echo "Installing whisper.cpp library..."
mkdir -p temp
cd temp

echo "Cloning whisper.cpp repository..."
if [ ! -d "whisper.cpp" ]; then
    git clone https://github.com/ggerganov/whisper.cpp.git
fi

cd whisper.cpp

echo "Building whisper.cpp library..."
# Build with optimizations for macOS
make

echo "Installing whisper.cpp library..."
# Copy the library to the appropriate location
mkdir -p /usr/local/lib
sudo cp libwhisper.dylib /usr/local/lib/ || sudo cp libwhisper.so /usr/local/lib/

echo "Creating symlinks..."
# Create necessary symlinks if needed
if [ -f "/usr/local/lib/libwhisper.dylib" ]; then
    sudo ln -sf /usr/local/lib/libwhisper.dylib /usr/local/lib/libwhisper.so
fi

echo "Updating library path..."
# Make sure the library can be found
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

echo "Installation completed. You may need to restart your application." 