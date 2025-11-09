// Auto-generated Cloudflare Worker from ozempic_classifier_optimized.json

export default {
    async fetch(request, env) {
        const url = new URL(request.url);

        if (!env.AI) {
            return Response.json({ error: "AI binding not configured" }, { status: 503 });
        }

        // Get input from query params
        const inputText = url.searchParams.get("input")
                       || url.searchParams.get("text")
                       || url.searchParams.get("complaint");

        // If no input, show API info
        if (!inputText) {
            return Response.json({
                name: "ozempic_classifier_optimized API",
                model: "openai/gpt-oss-120b",
                instructions: "Classify Ozempic-related complaints as Adverse Event or Product Complaint.",
                usage: "?input=your_text_here",
                example: "?input=" + encodeURIComponent("example text")
            });
        }

        // Call Cloudflare AI
        const aiResponse = await env.AI.run("@cf/openai/gpt-oss-20b", {
            instructions: `Classify Ozempic-related complaints as Adverse Event or Product Complaint.`,
            input: `Complaint: ${inputText}`
        });

        return Response.json({
            input: inputText,
            ai_response: aiResponse.response || aiResponse,
            model: "@cf/openai/gpt-oss-20b",
            artifact: "ozempic_classifier_optimized"
        });
    }
};
