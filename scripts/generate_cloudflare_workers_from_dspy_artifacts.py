#!/usr/bin/env python3
"""Generate Cloudflare Workers from DSPy artifacts.

This script converts DSPy classifier artifacts (JSON) into Cloudflare Workers
that can be deployed to the edge. Each artifact gets its own worker directory
with the worker code and wrangler.toml configuration.
"""

import json
from pathlib import Path

ARTIFACTS_DIR = Path(__file__).parent.parent / "artifacts"
OUTPUT_DIR = Path(__file__).parent.parent / "cloudflare" / "workers"


def generate_worker(artifact_path: Path) -> str:
    """Generate a Cloudflare Worker from a DSPy artifact."""
    with open(artifact_path) as f:
        artifact = json.load(f)

    signature = artifact["classify.predict"]["signature"]
    instructions = signature["instructions"]
    model = artifact["metadata"]["model"]
    fields = signature["fields"]

    # Extract input field (first field) and its name
    input_field = fields[0]
    input_name = input_field["prefix"].rstrip(":").lower().replace(" ", "_")

    # Map to Cloudflare AI model
    cf_model = "@cf/openai/gpt-oss-20b"

    return f'''// Auto-generated Cloudflare Worker from {artifact_path.name}

export default {{
    async fetch(request, env) {{
        const url = new URL(request.url);

        if (!env.AI) {{
            return Response.json({{ error: "AI binding not configured" }}, {{ status: 503 }});
        }}

        // Get input from query params
        const inputText = url.searchParams.get("input")
                       || url.searchParams.get("text")
                       || url.searchParams.get("{input_name}");

        // If no input, show API info
        if (!inputText) {{
            return Response.json({{
                name: "{artifact_path.stem} API",
                model: "{model}",
                instructions: "{instructions}",
                usage: "?input=your_text_here",
                example: "?input=" + encodeURIComponent("example text")
            }});
        }}

        // Call Cloudflare AI
        const aiResponse = await env.AI.run("{cf_model}", {{
            instructions: `{instructions}`,
            input: `{input_field["prefix"]} ${{inputText}}`
        }});

        return Response.json({{
            input: inputText,
            ai_response: aiResponse.response || aiResponse,
            model: "{cf_model}",
            artifact: "{artifact_path.stem}"
        }});
    }}
}};
'''


def generate_wrangler_config(artifact_name: str) -> str:
    """Generate wrangler.toml for the worker."""
    return f'''name = "{artifact_name.replace("_", "-")}"
main = "index.js"
compatibility_date = "2024-11-01"

[ai]
binding = "AI"
'''


def main():
    """Generate workers from all artifacts."""
    artifacts = list(ARTIFACTS_DIR.glob("*.json"))
    if not artifacts:
        print(f"No artifacts found in {ARTIFACTS_DIR}")
        return

    print(f"Found {len(artifacts)} artifact(s)\n")

    generated_workers = []
    for artifact_path in artifacts:
        print(f"Generating worker for {artifact_path.name}...")

        # Create worker directory
        worker_dir = OUTPUT_DIR / artifact_path.stem
        worker_dir.mkdir(parents=True, exist_ok=True)

        # Generate worker (as index.js for wrangler convention)
        worker_code = generate_worker(artifact_path)
        worker_path = worker_dir / "index.js"
        worker_path.write_text(worker_code)
        print(f"  ✓ {worker_path.relative_to(Path.cwd())}")

        # Generate wrangler config
        config = generate_wrangler_config(artifact_path.stem)
        config_path = worker_dir / "wrangler.toml"
        config_path.write_text(config)
        print(f"  ✓ {config_path.relative_to(Path.cwd())}")

        generated_workers.append(worker_dir)

    print(f"\n{'=' * 60}")
    print("✅ Done! All workers generated.")
    print(f"{'=' * 60}")

    for worker_dir in generated_workers:
        print(f"\n📦 {worker_dir.name}:")
        print("   To test locally:")
        print(f"     cd {worker_dir}")
        print("     wrangler dev")
        print("\n   To deploy:")
        print(f"     cd {worker_dir}")
        print("     wrangler deploy")


if __name__ == "__main__":
    main()
