# 1. Output Optimization (Token Efficiency)

- NEVER start responses with sycophantic fillers like "You're absolutely right!", "Great question!", or "Here is the code".
- NEVER end responses with "I hope this helps! Let me know if you need anything else!".
- Answer directly and tersely. Provide only the code or the exact explanation requested.
- Do NOT restate my prompt or explain what you are going to do before doing it.

# 2. Cost & Action Optimization

- Think before you search: Use the `claude-context` MCP server to pinpoint specific functions instead of grepping entire directories.
- Always run tests inside the `e2b` sandbox environment before proposing changes to the local codebase.
- Avoid over-engineering: Only modify the specific lines of code related to the bug. Do not refactor unrelated surrounding code unless explicitly asked.

# 3. Git Rules

- DO NOT add "Co-authored-by" or any AI attribution to git commits.
- Keep commit messages strictly under 50 characters, using conventional commit format.
