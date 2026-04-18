<div align="center">
  <h1>🤖 AutoReadme AI</h1>
  <p><b>Keep your documentation perfectly in sync with your codebase, without the developer friction.</b></p>

  <p>
    <a href="https://github.com/Michael-Steenkamp/repo-readme-generator/actions"><img src="https://img.shields.io/badge/GitHub%20Actions-Active-blue.svg" alt="GitHub Actions Workflow Status"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.x-blue.svg" alt="Python Version"></a>
    <a href="https://github.com/Michael-Steenkamp/repo-readme-generator/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
    <a href="https://github.com/Michael-Steenkamp/repo-readme-generator/releases/latest"><img src="https://img.shields.io/badge/Release-v1.0.0-blue" alt="Action Release"></a>
  </p>
</div>

<hr>

<h2>📖 Overview</h2>
<p>
  <b>AutoReadme AI</b> is a server-less Git automation pipeline and developer tool designed to eliminate the chore of manual documentation updates. It dynamically fetches your project's state, requests intelligent documentation updates from Large Language Models (LLMs), and seamlessly utilizes the GitHub API to submit code changes via Pull Requests.
</p>
<p>
  Stop writing READMEs. Start shipping code.
</p>

<hr>

<h2>🏗️ Architecture & Phases of Development</h2>
<p>The AutoReadme AI pipeline executes in three distinct, highly optimized phases:</p>

<h3>Phase A: Environment & Extraction</h3>
<ul>
  <li><b>Diff Extraction:</b> Extracts the latest Git diff (<code>HEAD~1 HEAD</code>) using standard Python libraries.</li>
  <li><b>Tree Generation:</b> Generates a token-efficient directory tree of your project.</li>
  <li><b>Custom Rules:</b> Applies custom exclusion rules via a <code>.autoreadme.yml</code> configuration file to ignore irrelevant files.</li>
  <li><b>State Parsing:</b> Parses the current <code>README.md</code> to extract hidden AI state memory for continuous context.</li>
</ul>

<h3>Phase B: The AI Pipeline</h3>
<ul>
  <li><b>Payload Compilation:</b> Compiles a strict, context-rich prompt payload.</li>
  <li><b>Tiered LLM Routing:</b> Intelligently routes the request based on payload size—sending small diffs to fast models (like Gemini 2.5 Flash) and massive architectural shifts to heavy models (like GPT-4o).</li>
  <li><b>State Injection:</b> Injects the rolling-state memory so the AI remembers past decisions.</li>
  <li><b>Execution & Sanitization:</b> Enforces a strict raw-markdown output instruction and actively sanitizes the response using Regex to strip rogue formatting, backticks, or hallucinations.</li>
</ul>

<h3>Phase C: Version Control Reconciliation</h3>
<ul>
  <li><b>Cloud Execution:</b> Utilizes GitHub Actions to run the pipeline on push, automatically opening a new PR with updated documentation.</li>
</ul>

<hr>

<h2>✨ Key Features</h2>
<ul>
  <li>📦 <b>Plug-and-Play Action:</b> Easily integrate into any repository via a single <code>uses</code> step. No need to clone scripts or manage dependencies.</li>
  <li>🧠 <b>Rolling-State Memory:</b> Maintains context across pushes without an external database by using hidden HTML comments embedded directly in the README.</li>
  <li>📏 <b>Smart Git Diffing:</b> Automatically falls back to a <code>--stat</code> summary if code changes are massive, protecting your API costs and preventing token limit breaches.</li>
  <li>🔀 <b>Tiered LLM Routing:</b> Dynamically selects the most efficient AI provider based on the character length of the git diff.</li>
  <li>⚡ <b>Zero-Dependency Core:</b> Built entirely using standard Python libraries to ensure lightning-fast execution and zero environment bloating.</li>
</ul>

<hr>

<h2>🚀 Getting Started</h2>
<p>
  Integrate AutoReadme AI directly into your repository using the official GitHub Action. This runs entirely in the cloud, automatically opening PRs with documentation updates whenever you push code.
</p>

<h3>1. Initialize the Repository</h3>
<p>
  Create your new repository on GitHub and clone it locally. You do not even need a <code>README.md</code> to start, as the engine will intelligently generate a fresh one!
</p>

<h3>2. Grant Pull Request Permissions</h3>
<p>
  Before adding any code, configure the repository settings so the Action is legally allowed to open PRs.
</p>
<ul>
  <li>Go to your repository on GitHub.</li>
  <li>Navigate to <b>Settings</b> > <b>Actions</b> > <b>General</b>.</li>
  <li>Scroll down to the <b>Workflow permissions</b> section.</li>
  <li>Check the box for <b>Allow GitHub Actions to create and approve pull requests</b>.</li>
  <li>Click <b>Save</b>.</li>
</ul>

<h3>3. Add Your API Keys (Repository Secrets)</h3>
<p>
  You need to securely store your API keys so the GitHub runner can access them during execution. You only need to add keys for the specific models you plan to route to.
</p>
<p><b>Via the Web UI:</b></p>
<ul>
  <li>Go to <b>Settings</b> > <b>Security</b> > <b>Secrets and variables</b> > <b>Actions</b>.</li>
  <li>Click the green <b>New repository secret</b> button.</li>
  <li>Name it exactly <code>GEMINI_API_KEY</code> and paste your key.</li>
  <li><i>(Optional)</i> Repeat for <code>OPENAI_API_KEY</code> or <code>ANTHROPIC_API_KEY</code> if you are setting up multi-model routing.</li>
</ul>
<p><b>Via the Terminal:</b></p>
<p>If you prefer a keyboard-driven workflow, you can inject secrets directly using the GitHub CLI:</p>

```bash
gh secret set GEMINI_API_KEY --body "your_actual_api_key_here"
```

<h3>4. Add the Workflow</h3>
<p>Create a new file in your repository at <code>.github/workflows/autoreadme.yml</code> and add the following configuration:</p>

```yml
name: AI Documentation Update
on:
  push:
    branches: [ main ]
    paths-ignore: ['README.md'] # Prevents infinite loops!
  workflow_dispatch:

permissions:
  contents: write
  pull-requests: write

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps: 
      - name: Checkout Code
        uses: actions/checkout@v4 
        with: 
          fetch-depth: 2 
          
      - name: Run AutoReadme AI
        uses: Michael-Steenkamp/repo-readme-generator@v1
        with: 
          gemini-api-key: ${{ secrets.GEMINI_API_KEY }}
          # Uncomment below if you set up heavy routing secrets
          # openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          # anthropic-api-key: ${{ secrets.ANTHROPIC_API_KEY }}
```

<h3>5. Push and Trigger!</h3>
<p>
  Commit your new workflow file and push it to the <code>main</code> branch.
</p>
<p>
  Because your workflow is set to trigger <code>on: push</code>, this initial push will instantly wake up the GitHub Action. It will pull your code, utilize your API key to generate a brand new README based on your project's tree, and automatically open a Pull Request for you to merge!
</p>


<!-- AI_STATE_START
{
  "summary": "AutoReadme AI's core architecture is fully implemented, encompassing environment extraction, tiered LLM routing for documentation generation, and version control reconciliation. The `extract_state` function in `script/update_readme.py` has been enhanced to robustly parse the hidden AI state from the README, ensuring the latest state block is correctly identified and handled, and providing error detection for malformed JSON. The system continues to feature regex-based output sanitization, zero-dependency Python execution, and comprehensive setup for both Cloud (GitHub Actions) and Local `git autopush` workflows."
}
AI_STATE_END -->
