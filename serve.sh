#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: ./serve.sh -m /path/to/model.gguf"
    exit 1
fi

if [ "$1" != "-m" ] || [ -z "$2" ]; then
    echo "Usage: ./serve.sh -m /path/to/model.gguf"
    exit 1
fi

MODEL_PATH="$2"

# Switch parakeet to CPU mode to free up vRAM for llama
echo "[serve.sh] Switching parakeet to CPU mode..."
systemctl --user stop parakeet-tdt-0.6b-v3.service 2>/dev/null
PARAKEET_USE_CPU=1 systemctl --user set-environment PARAKEET_USE_CPU=1
systemctl --user start parakeet-tdt-0.6b-v3.service

# Restore parakeet to GPU mode on exit
cleanup() {
    echo ""
    echo "[serve.sh] Restoring parakeet to GPU mode..."
    systemctl --user stop parakeet-tdt-0.6b-v3.service 2>/dev/null
    systemctl --user unset-environment PARAKEET_USE_CPU
    systemctl --user start parakeet-tdt-0.6b-v3.service
    echo "[serve.sh] Parakeet restored to GPU mode"
}
trap cleanup EXIT INT TERM

~/llama.cpp/build/bin/llama-server \
    -m "$MODEL_PATH" \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 999 `# offload all layers to GPU` \
    -fa on `# flash attention - faster, less VRAM` \
    -c 32768 `# total context (divided across parallel slots)` \
    -np 4 `# parallel slots for concurrent requests (8K ctx each)` \
    -b 4096 `# logical batch size` \
    -ub 1024 `# physical GPU batch size, tune for VRAM` \
    -ctk q8_0 `# quantize KV cache keys - saves VRAM` \
    -ctv q8_0 `# quantize KV cache values - saves VRAM` \
    --mlock `# lock model in RAM, prevent swapping` \
    -t 8 # CPU threads for generation
