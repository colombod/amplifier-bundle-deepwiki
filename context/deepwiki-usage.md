# DeepWiki Usage Patterns

Tool-specific best practices and exploration strategies for DeepWiki's MCP tools.

---

## Tool-Specific Guidance

### ask_question (START HERE)

**Purpose:** Ask natural language questions and get AI-powered, context-grounded answers.

**This is your primary tool.** DeepWiki's AI has already processed the entire 
codebase - leverage that instead of reading raw content.

**Best practices:**
- **Break down complex questions** - Multiple simple questions > one complex question
- Simple questions: 5-15 seconds
- Complex/synthesis questions: 30-60+ seconds (may timeout)
- Be specific about what aspect you need

**Progressive question strategy:**

```
1. "What is [library] and what problem does it solve?"     ← Start here
2. "What are the main components of [library]?"            ← Build context  
3. "How does [specific component] work?"                   ← Go deeper
4. "How do I extend [specific feature]?"                   ← Practical goal
```

**Effective question patterns:**

| Pattern | Example |
|---------|---------|
| Overview | "What are the main components of the FastAPI framework?" |
| Specific | "How does React's useState hook work internally?" |
| Practical | "How do I add a custom middleware to Express?" |
| Comparison | "How does Vue's reactivity differ from React's?" |

**Avoid (causes timeouts):**
- "Tell me everything about React's architecture, internals, and extension points"
- Multiple unrelated questions in one request
- Vague questions: "How does it work?"

---

### read_wiki_structure

**Purpose:** Get the hierarchical outline of available documentation.

**When to use:**
- Planning a systematic deep dive
- Need to know what topics exist
- Looking for specific sections to explore

**Best practices:**
- Fast operation (2-5 seconds)
- Use to identify relevant sections for follow-up questions
- Helps you ask better targeted questions

**Example response:**
```
- Overview
- Core Architecture
  - Kernel System
  - Command and Event System
- Features
  - Magic Commands
  - Variable Sharing
- API Reference
```

---

### read_wiki_contents

**Purpose:** Read the full wiki content for a repository.

**Parameters:** Only `repoName` (owner/repo format). Does NOT support page filtering.

**When to use:**
- Need exhaustive, comprehensive content
- Questions aren't giving enough detail
- Want to search for specific terms across all docs

**Characteristics:**
- Returns ALL wiki pages concatenated (can be 400k+ chars)
- Content is automatically truncated to ~50k chars
- Pages separated by `# Page: <Page Name>` headers
- Includes Mermaid diagrams, tables, source references

**Best practices:**
- Use AFTER questions have narrowed your focus
- Search within returned content for specific terms
- Look for `[src/path/file.cs:line-range]()` references

---

## Exploration Strategies

### Progressive Discovery (Recommended)

**For any new project exploration:**

```
Phase 1: Quick Understanding (2-3 questions)
├─ "What is [repo] and what problem does it solve?"
├─ "What are the main architectural components?"
└─ "How do I typically use/extend it?"

Phase 2: Targeted Deep Dive (if needed)
├─ Get structure to see available topics
├─ Ask specific questions about relevant sections
└─ Read content only for sections needing exhaustive detail

Phase 3: Practical Application
├─ "How do I implement [specific goal]?"
├─ "What are the extension points for [feature]?"
└─ "Show me the pattern for [use case]"
```

### Understanding Architecture

1. **Quick overview** → `ask_question`: "What's the architecture of [repo]?"
2. **Identify components** → `ask_question`: "What are the main modules?"
3. **Deep dive** → `ask_question`: "How does [specific component] work?"
4. **Verify** → `read_wiki_structure` to see if you missed anything

### Finding Extension Points

1. **Direct question** → "How do I extend [library] to add [feature]?"
2. **Follow up** → "What interfaces/protocols do I need to implement?"
3. **Examples** → "Show me the pattern for creating a custom [thing]"
4. **Structure check** → Look for "Extensions", "Plugins", "API" sections

### Quick Understanding (Time-Limited)

1. **Single question** → "What is [library] and how does it work?"
2. **Follow up only if needed** → Ask about the specific aspect that matters
3. Done - don't over-explore if you have what you need

---

## Handling Timeouts

Complex questions may timeout. When this happens:

1. **Break down the question** into simpler parts
2. **Ask incrementally** - build context through multiple questions
3. **Be more specific** - narrow the scope

**Instead of:**
> "Explain the complete command and event system architecture"

**Try:**
> 1. "What command types exist in the system?"
> 2. "What event types are emitted?"  
> 3. "How does command routing work?"

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Starting with read_wiki_contents | Start with questions instead |
| Asking overly complex questions | Break into progressive simple questions |
| Waiting for timeouts | If >30s, break down the question |
| Reading everything | Let questions guide what you need |
| Missing the big picture | Always start with overview question |


