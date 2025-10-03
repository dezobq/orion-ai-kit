# SPDX-License-Identifier: Apache-2.0
#!/usr/bin/env python3
# Example wiring with Anthropic SDK (pseudo); install anthropic and set ANTHROPIC_API_KEY
from anthropic import Anthropic
from memory_tool import MemoryTool
mem = MemoryTool()
client = Anthropic()
TOOLS = [{"type": "memory_20250818", "name": "memory"}]
# See docs for streaming loop to handle tool_use and send tool_result.
