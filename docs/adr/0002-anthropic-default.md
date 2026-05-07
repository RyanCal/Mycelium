# ADR 0002: Anthropic Default

Anthropic is the default LLM provider. Access is isolated behind provider
adapters so cheaper or local models can be added later without changing agents.
Prompt caching is enabled by default for stable system context.
