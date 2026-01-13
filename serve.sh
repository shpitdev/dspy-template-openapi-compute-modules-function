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
