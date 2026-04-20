import re
import json
import subprocess
import os
import fnmatch
import yaml
from collections import defaultdict
import urllib.request
import urllib.error
import argparse
import sys
import time

def extract_state(readme_text):
    pattern = r'<' + r'!-- AI_STATE_START(.*?)AI_STATE_END --' + r'>'
    matches = re.findall(pattern, readme_text, re.DOTALL)
    
    # Check if the regex found any matches before accessing the list
    if not matches:
        print("[AutoReadme] No AI state block found. Initializing fresh state.")
        return {"summary": "New project."}
        
    # The actual AI state block should always be the last one in the file
    raw_state = matches[-1].strip()
    try:
        return json.loads(raw_state)
    except json.JSONDecodeError as e:
        print(f"[AutoReadme] Warning: State block found but JSON is invalid: {e}")
            
    return {"summary": "New project."}

def get_git_diff(diff_target="HEAD~1 HEAD", max_chars=10000):
    """Extracts the git diff based on the provided target (e.g., HEAD~1 HEAD)."""
    try:
        # Split target so subprocess safely reads it as separate arguments
        diff_args = diff_target.split()
        
        # Explicit utf-8 encoding and error replacement for Windows compatibility
        result = subprocess.run(
            ['git', 'diff'] + diff_args, 
            capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
        )
        diff_text = result.stdout
        
        if len(diff_text) > max_chars:
            stat_result = subprocess.run(
                ['git', 'diff', '--stat'] + diff_args,
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
            )
            return (
                f"[SYSTEM LOG: Full diff exceeded {max_chars} characters. "
                f"Providing skimmed file stat summary instead.]\n\n"
                f"{stat_result.stdout}"
            )
        return diff_text
    except subprocess.CalledProcessError:
        return "Initial commit or insufficient commit history for diff."

def load_config():
    """Loads custom routing, pattern rules, and style directives from .autoreadme.yml"""
    # Base defaults if the user hasn't created a config file
    config = {
        "includePatterns": [], 
        "excludePatterns": [".github/**", "node_modules/**", "__pycache__/**"],
        "routing": {
            "threshold_chars": 1500,
            "fast_provider": "gemini",
            "heavy_provider": "openai"
        },
        "style": {
            "theme": "developer-first",
            "include_badges": True
        }
    }
    
    try:
        if os.path.exists('.autoreadme.yml'):
            with open('.autoreadme.yml', 'r') as f:
                user_config = yaml.safe_load(f) or {}
                if "includePatterns" in user_config:
                    config["includePatterns"] = user_config["includePatterns"]
                if "excludePatterns" in user_config:
                    config["excludePatterns"] = user_config["excludePatterns"]
                if "routing" in user_config:
                    config["routing"].update(user_config["routing"])
                if "style" in user_config:
                    config["style"].update(user_config["style"])
    except Exception as e:
        print(f"Warning: Could not parse .autoreadme.yml, using defaults. Error: {e}")
        
    return config

def route_llm_payload(prompt, diff_text, config):
    """Dynamically routes the prompt to the appropriate LLM based on task size."""
    routing_config = config.get("routing", {})
    threshold = routing_config.get("threshold_chars", 1500)
    
    # Determine task size and assign provider
    diff_size = len(diff_text)
    if diff_size < threshold:
        provider = routing_config.get("fast_provider", "gemini").lower()
        print(f"[Router] Diff size ({diff_size} chars) is under threshold. Routing to Fast Model: {provider.upper()}")
    else:
        provider = routing_config.get("heavy_provider", "openai").lower()
        print(f"[Router] Diff size ({diff_size} chars) exceeds threshold. Routing to Heavy Model: {provider.upper()}")
        
    # Dispatch the payload
    return dispatch_request(prompt, provider)

def dispatch_request(prompt, provider):
    """Compiles provider-specific payloads and executes the HTTP request."""
    system_instruction = "You are an AI that exclusively outputs raw Markdown. Do not include conversational filler."
    max_retries = 6 # 1 initial attempt + 5 retries
    delays = [1, 2, 4, 8, 16]
    
    for attempt in range(max_retries):
        try:
            if provider == "openai":
                api_key = os.environ.get("OPENAI_API_KEY")
                url = "https://api.openai.com/v1/chat/completions"
                data = {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": prompt}
                    ]
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }
                
            elif provider == "gemini":
                api_key = os.environ.get("GEMINI_API_KEY")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                data = {
                    "systemInstruction": { "parts": [{"text": system_instruction}]},
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                headers = {"Content-Type": "application/json"}
                
            elif provider == "anthropic":
                api_key = os.environ.get("ANTHROPIC_API_KEY")
                url = "https://api.anthropic.com/v1/messages"
                data = {
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 2000,
                    "system": system_instruction,
                    "messages": [{"role": "user", "content": prompt}]
                }
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01"
                }
            else:
                return f"Error: Unsupported provider '{provider}'"

            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers, method='POST')
            
            if not api_key:
                 return f"[Local Test] Route successful. Payload configured for {provider.upper()}, but no API key found in environment."

            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if provider == "openai":
                    return result['choices'][0]['message']['content']
                elif provider == "gemini":
                    return result['candidates'][0]['content']['parts'][0]['text']
                elif provider == "anthropic":
                    return result['content'][0]['text']

        except urllib.error.HTTPError as e:
            # Handle temporary network/server overloads with retries (quietly in the background)
            if e.code in [429, 500, 502, 503, 504] and attempt < len(delays):
                time.sleep(delays[attempt])
                continue
                
            # Fallback to fast model on HTTP failure if we exhaust retries (or hit a non-retryable error)
            if provider != "gemini":
                print(f"[Router Warning] {provider.upper()} failed with {e.code}. Initiating failover to Fast Model...")
                return dispatch_request(prompt, "gemini")
            return f"API Connection Error: {e.code} - {e.reason}. Please try again later."
            
        except urllib.error.URLError as e:
            if attempt < len(delays):
                time.sleep(delays[attempt])
                continue
            return f"API Connection Error: {e}"
            
    return "API Connection Error: Maximum retries exceeded."

def match_pattern(file_path, pattern):
    """Translates glob patterns (like **/*.md or .mvn/**) for Python's fnmatch"""
    if pattern.endswith('/**'):
        prefix = pattern[:-3]
        if file_path.startswith(prefix + '/') or file_path == prefix:
            return True
            
    clean_pattern = pattern.replace('**/', '') 
    return fnmatch.fnmatch(file_path, clean_pattern) or fnmatch.fnmatch(file_path, f"*/{clean_pattern}")

def get_project_tree(diff_target="HEAD~1 HEAD"):
    """Generates a directory-level summary using custom .autoreadme.yml rules."""
    try:
        config = load_config()
        
        # Explicit utf-8 encoding and error replacement for Windows
        all_files_result = subprocess.run(
            ['git', 'ls-files'], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
        )
        all_files = [f for f in all_files_result.stdout.strip().split('\n') if f]

        try:
            diff_args = diff_target.split()
            diff_result = subprocess.run(
                ['git', 'diff', '--name-only'] + diff_args, 
                capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
            )
            modified_files = set(f for f in diff_result.stdout.strip().split('\n') if f)
        except subprocess.CalledProcessError:
            modified_files = set() # Failsafe for initial commits

        dir_stats = defaultdict(lambda: {"count": 0, "exts": set(), "modified": False})
        
        for file_path in all_files:
            # Apply Exclusion Rules
            if any(match_pattern(file_path, excl) for excl in config["excludePatterns"]):
                continue
                
            # Apply Inclusion Rules
            if config["includePatterns"]:
                if not any(match_pattern(file_path, incl) for incl in config["includePatterns"]):
                    continue
                
            directory = os.path.dirname(file_path) or "." 
            ext = os.path.splitext(file_path)[1] or "(no ext)"
            
            dir_stats[directory]["count"] += 1
            dir_stats[directory]["exts"].add(ext)
            
            if file_path in modified_files:
                dir_stats[directory]["modified"] = True

        tree_lines = ["Project Structure (Summarized by Directory):"]
        for directory, stats in sorted(dir_stats.items()):
            ext_str = ", ".join(sorted(list(stats["exts"])))
            mod_flag = " [MODIFIED]" if stats["modified"] else ""
            tree_lines.append(f"  {directory}/ -> {stats['count']} files ({ext_str}){mod_flag}")
            
        return "\n".join(tree_lines)
        
    except subprocess.CalledProcessError:
        return "Error: Could not extract project tree."
    
def clean_llm_output(raw_text):
    """
    Strips rogue markdown wrappers and trailing whitespace from the LLM response.
    Specifically removes ```markdown from the start and ``` from the end.
    """
    clean_text = re.sub(r'^```[a-zA-Z]*\s*\n', '', raw_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\n\s*```\s*$', '', clean_text)
    return clean_text.strip() + '\n'
    
if __name__ == "__main__":
    # --- NEW: Command Line Interface Setup ---
    parser = argparse.ArgumentParser(description="AutoReadme AI Engine")
    parser.add_argument("--diff", type=str, default="HEAD~1 HEAD", help="Specify Git diff range (e.g., 'HEAD~1 HEAD' or 'HEAD~3 HEAD')")
    parser.add_argument("--force", action="store_true", help="Force README generation even if the git diff is empty.")
    args = parser.parse_args()

    print(f"[AutoReadme] Initializing local generation... (Target: {args.diff})")
    
    # Gather context
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            current_readme = f.read()
    except FileNotFoundError:
        current_readme = "# New Project\n"

    state = extract_state(current_readme)
    config = load_config()
    diff_text = get_git_diff(args.diff)
    project_tree = get_project_tree(args.diff)
    
    # Check for empty diffs, unless --force is applied
    if not args.force and ("Initial commit" in diff_text or not diff_text.strip()):
        print("[AutoReadme] No valid diff found. Skipping generation. (Use --force to override)")
        sys.exit(0)
        
    # If forced, we manually inject a placeholder to ensure the AI knows why it was triggered
    if args.force and not diff_text.strip():
        print("[AutoReadme] Force flag detected. Bypassing empty diff check...")
        diff_text = "[SYSTEM LOG: Forced regeneration. No specific code diff provided. Please rely entirely on the Project Tree and Current README State.]"

    # Compile Style Parameters
    style_config = config.get("style", {})
    theme = style_config.get("theme", "developer-first")
    include_badges = style_config.get("include_badges", True)
    
    # --- ENHANCED: Give the AI strict HTML styling rules for badges ---
    badge_instruction = (
        "Include relevant standard Markdown badges (e.g., using shields.io for language, build status, license). "
        "Integrate them stylistically at the very top of the document (e.g., grouped neatly and centered using HTML `<div align=\"center\">` tags directly under the main title) rather than randomly placing them."
    ) if include_badges else "Do NOT include any Markdown badges. Keep the visual style purely text-based."

    # --- ENHANCED: Change "Rebuild" to "Update" and add the Surgical Update rule ---
    USER_PROMPT = f"""
    You are an expert technical writer. Your task is to strategically UPDATE the existing README.md based on the provided Git Diff and Project Tree.

    --- CONTEXT INJECTIONS ---

    1. CURRENT AI STATE:
    {json.dumps(state)}

    2. PROJECT TREE:
    {project_tree}

    3. LATEST GIT DIFF:
    {diff_text}

    4. CURRENT README:
    {current_readme}
    
    --- STYLE DIRECTIVES ---
    Theme/Tone: {theme}
    Badges: {badge_instruction}

    --- EXECUTION RULES ---
    1. SURGICAL UPDATE: Do NOT rewrite the entire README from scratch. Preserve the existing layout, HTML structure, headings, and unique styling of the CURRENT README. Only add or modify the specific sections relevant to the LATEST GIT DIFF.
    2. Synthesize the Git Diff into the README seamlessly. Do not invent features or document files that do not exist in the Project Tree.
    3. Maintain a {theme} tone.
    4. {badge_instruction}
    5. Update the rolling summary to reflect these new changes.
    6. You MUST append this new rolling summary at the absolute bottom of your response, strictly formatted as hidden HTML.

    Format the state block EXACTLY like this at the end of the file:
    <!-- AI_STATE_START
    {{
      "summary": "Concise summary of the current project state and the latest updates."
    }}
    AI_STATE_END -->
    """

    # Dispatch Request
    print(f"[AutoReadme] Compiling prompt (Theme: {theme}) and routing to LLM...")
    raw_response = route_llm_payload(USER_PROMPT, diff_text, config)
    
    if raw_response.startswith("API Connection Error") or "Error:" in raw_response:
        print(f"[AutoReadme] Generation failed: {raw_response}")
        sys.exit(1)

    # --- NEW: SAFEGUARD AGAINST MISSING API KEYS ---
    if "[Local Test]" in raw_response:
        print("[AutoReadme] 🛑 Local test detected (No API key found in environment).")
        print("[AutoReadme] Aborting file write to protect README from being overwritten.")
        sys.exit(0)

    # Sanitize the output to remove rogue backticks
    new_readme_content = clean_llm_output(raw_response)

    # Output to File
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme_content)
        
    print("[AutoReadme] README.md successfully updated!")