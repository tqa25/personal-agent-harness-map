# Use a replaceable Search Provider

The Personal Copilot requires complete Web Research with Source Comparison, but web search backends vary by model provider, account access, result quality, and API limits. We will default V1 to Microsoft hosted web search when available, while keeping Web Research behind a replaceable Search Provider so the system can switch to OpenAI, Tavily, Brave, SerpAPI, or another backend without changing the copilot's domain behavior.
