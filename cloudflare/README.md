# Cloudflare Workers for DSPy Artifacts

Quick way to take your optimized DSPy artifacts and deploy them as Cloudflare AI Workers. They're fast, lightweight, and
run at the edge (300+ cities worldwide).

## Quick Start

### 1. Generate Workers

```bash
python3 scripts/generate_cloudflare_workers_from_dspy_artifacts.py
```

This scans `artifacts/*.json` and creates Cloudflare Workers in `cloudflare/workers/<worker-name>/`. Each worker gets
its own directory with `index.js` and `wrangler.toml`.

### 2. Test Locally

```bash
cd cloudflare/workers/ozempic_classifier_optimized
wrangler dev
```

Opens at `http://localhost:8787`

**Test in browser:**

```bash
http://localhost:8787/?input=I had severe nausea after taking Ozempic
```

**Or with curl:**

```bash
curl "http://localhost:8787/?input=I%20had%20severe%20nausea"
```

### 3. Deploy

```bash
# First time only
wrangler login

# Deploy
cd cloudflare/workers/ozempic_classifier_optimized
wrangler deploy
```

You'll get a URL like: `https://ozempic-classifier-optimized.your-subdomain.workers.dev`

## What Gets Generated

For each artifact in `artifacts/`, you get a directory structure:

```
cloudflare/workers/
└── ozempic_classifier_optimized/
    ├── index.js          # The worker script
    └── wrangler.toml     # Deployment config
```

## API

Simple GET-only API at the root path:

- **`/?input=your_text`** - Process input (works in browser!)
- **`/`** - Show API info (when no input provided)

The response includes the raw AI response plus metadata. Works for any artifact type!

## Why Cloudflare Workers?

- ⚡ **Fast** - 50ms cold starts vs 2-5s for containers
- 🌍 **Global** - Runs in 300+ cities
- 💰 **Cheap** - Free tier: 100k requests/day
- 🔒 **Simple** - No servers to manage
- 🌐 **GET-only** - Test by pasting URLs in browser!

## Example Response

```json
{
  "input": "I had severe nausea after taking Ozempic",
  "ai_response": "Classification: Adverse Event\n\nJustification: The complaint describes a physiological reaction...",
  "model": "@cf/meta/llama-2-7b-chat-int8",
  "artifact": "ozempic_classifier_optimized"
}
```

## Testing

Just paste a URL in your browser or use curl:

```bash
# Test locally
curl "http://localhost:8787/?input=test%20this"

# Test deployed
curl "https://your-worker.workers.dev/?input=test%20this"
```

## How It Works

The generator reads your artifact and automatically:

1. Extracts the first field as the input (e.g., "Complaint:", "Text:", etc.)
2. Builds a prompt using the artifact's instructions
3. Creates a simple GET-only worker
4. Returns the raw AI response

**Completely agnostic!** Works for classifying complaints, analyzing fried chicken reviews, or anything else. Just paste
a URL in your browser to test!

## Requirements

- Python 3.8+
- Wrangler CLI: `npm install -g wrangler`
- Cloudflare account (free tier works)

That's it! From DSPy artifact to global edge deployment in minutes.
