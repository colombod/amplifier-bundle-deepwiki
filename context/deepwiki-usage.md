# DeepWiki Usage Patterns

This document provides comprehensive guidance for effectively using DeepWiki 
to understand open-source projects.

## Repository Format

DeepWiki uses GitHub repository identifiers in `owner/repo` format:

| Example | Repository |
|---------|------------|
| `facebook/react` | React library |
| `tiangolo/fastapi` | FastAPI framework |
| `microsoft/vscode` | VS Code editor |
| `langchain-ai/langchain` | LangChain framework |
| `pallets/flask` | Flask framework |

**Important:** Only public GitHub repositories are accessible. Private repos 
require a Devin.ai account.

---

## Tool-Specific Guidance

### read_wiki_structure

**Purpose:** Get the hierarchical outline of available documentation for a repository.

**When to use:**
- Starting any exploration of a new repository
- Planning which sections to read in detail
- Understanding how documentation is organized

**Best practices:**
- Always start here before reading contents
- Look for sections matching the user's interests
- Note the hierarchy - parent sections provide context

**Example response structure:**
```
- Overview
  - Architecture
  - Key Concepts
- Getting Started
- Core Components
  - Component A
  - Component B
- Advanced Topics
  - Extension Points
  - Internals
```

---

### read_wiki_contents

**Purpose:** Read the full wiki content for a repository.

**Parameters:** Only `repoName` (owner/repo format). Does NOT support page filtering.

**When to use:**
- After identifying the repository you want to explore
- Need comprehensive documentation content
- Looking for code examples and implementation details

**Best practices:**
- Returns ALL wiki pages concatenated (can be 400k+ chars)
- Content is automatically truncated to ~50k chars by the tool
- Pages are separated by `# Page: <Page Name>` headers
- Each page includes "Relevant source files" sections

**Tips:**
- Content includes Mermaid diagrams, tables, and source references
- Look for `[src/path/file.cs:line-range]()` references for code locations
- If you need specific sections, search within the returned content

**Note:** This tool returns the entire wiki, not individual pages. Use 
`read_wiki_structure` first to understand what's available.

---

### ask_question

**Purpose:** Ask natural language questions and get AI-powered, context-grounded answers.

**When to use:**
- Specific "how" or "why" questions
- When you need synthesis across multiple topics
- Quick answers without reading full documentation

**Best practices:**
- Be specific about what you want to understand
- Include context about your goal
- Good for clarifying questions after reading docs

**Effective question patterns:**

| Pattern | Example |
|---------|---------|
| Implementation | "How does React implement the virtual DOM diffing algorithm?" |
| Design decisions | "Why does FastAPI use Pydantic for data validation?" |
| Extension | "What's the recommended way to add a custom middleware in Express?" |
| Comparison | "How does Vue's reactivity system differ from React's?" |
| Architecture | "What's the overall architecture of the LangChain framework?" |

**Avoid:**
- Overly broad questions: "Tell me everything about React"
- Vague questions: "How does it work?"
- Multiple unrelated questions in one

---

## Exploration Strategies

### Understanding Architecture (Deep Dive)

1. **Get structure** → `read_wiki_structure`
2. **Read overview** → `read_wiki_contents` on "Overview" or "Introduction"
3. **Read architecture** → `read_wiki_contents` on "Architecture" or "Design"
4. **Explore components** → Read individual component docs
5. **Clarify specifics** → `ask_question` for remaining questions

### Finding Extension Points (Practical Goal)

1. **Get structure** → Look for "Extensions", "Plugins", "Customization"
2. **Read extension docs** → `read_wiki_contents` on relevant sections
3. **Ask specific question** → "How do I create a custom X in this library?"
4. **Read examples** → Look for "Examples" sections

### Quick Understanding (Time-Limited)

1. **Ask broad question** → "What is [library] and how does it work?"
2. **Follow up** → Ask about specific aspects that matter
3. **Verify understanding** → Get structure and spot-check key sections

### Debugging Integration Issues

1. **Ask specific question** → "Why might [specific error/behavior] occur?"
2. **Read internals** → `read_wiki_contents` on relevant component
3. **Check edge cases** → Ask about common pitfalls

---

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Skipping structure exploration | Always start with `read_wiki_structure` |
| Asking overly broad questions | Be specific about what aspect you need |
| Reading random sections | Use structure to identify most relevant docs |
| Missing context | Read overview/architecture before diving deep |
| Single-source answers | Use multiple sections + ask_question for synthesis |

---

## Response Quality Checklist

Before returning to the user, ensure your response:

- [ ] Directly answers their question
- [ ] Uses the repository's terminology
- [ ] Cites specific documentation sections
- [ ] Includes practical guidance they can act on
- [ ] Suggests related topics for further exploration
- [ ] Is comprehensive enough to be useful
