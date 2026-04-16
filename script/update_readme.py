import re
import json
import subprocess
import os
import fnmatch
import yaml
from collections import defaultdict
import urllib.request
import urllib.error

def extract_state(readme_text):
    pattern = r'<' + r'!-- AI_STATE_START(.*?)AI_STATE_END --' + r'>'
    match = re.search(pattern, readme_text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    return {"summary": "New project."}

def get_git_diff(max_chars=10000):
    try:
        result = subprocess.run(
            ['git', 'diff', 'HEAD~1', 'HEAD'], 
            capture_output=True, text=True, check=True
        )
        diff_text = result.stdout
        
        if len(diff_text) > max_chars:
            stat_result = subprocess.run(
                ['git', 'diff', '--stat', 'HEAD~1', 'HEAD'],
                capture_output=True, text=True, check=True
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
    """Loads custom routing and pattern rules from .autoreadme.yml"""
    # Base defaults if the user hasn't created a config file
    config = {
        "includePatterns": [], 
        "excludePatterns": [".github/**", "node_modules/**", "__pycache__/**"]
    }
    
    try:
        if os.path.exists('.autoreadme.yml'):
            with open('.autoreadme.yml', 'r') as f:
                user_config = yaml.safe_load(f) or {}
                if "includePatterns" in user_config:
                    config["includePatterns"] = user_config["includePatterns"]
                if "excludePatterns" in user_config:
                    config["excludePatterns"] = user_config["excludePatterns"]
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
    
    # Standardize our expected output format
    system_instruction = "You are an AI that exclusively outputs raw Markdown. Do not include conversational filler."
    
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
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            data = {
                "system_instruction": { "parts": [{"text": system_instruction}]},
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
        # Fallback to fast model on HTTP failure
        if provider != "gemini":
            print(f"[Router Warning] {provider.upper()} failed with {e.code}. Initiating failover to Fast Model...")
            return dispatch_request(prompt, "gemini")
        return f"API Connection Error: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"API Connection Error: {e}"

def match_pattern(file_path, pattern):
    """Translates glob patterns (like **/*.md or .mvn/**) for Python's fnmatch"""
    if pattern.endswith('/**'):
        prefix = pattern[:-3]
        if file_path.startswith(prefix + '/') or file_path == prefix:
            return True
            
    clean_pattern = pattern.replace('**/', '') 
    return fnmatch.fnmatch(file_path, clean_pattern) or fnmatch.fnmatch(file_path, f"*/{clean_pattern}")

def get_project_tree():
    """Generates a directory-level summary using custom .autoreadme.yml rules."""
    try:
        config = load_config()
        
        all_files_result = subprocess.run(
            ['git', 'ls-files'], capture_output=True, text=True, check=True
        )
        all_files = [f for f in all_files_result.stdout.strip().split('\n') if f]

        try:
            diff_result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], 
                capture_output=True, text=True, check=True
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

if __name__ == "__main__":
    import sys
    print("[AutoReadme] Initializing local pre-push generation...")
    
    # Gather context
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            current_readme = f.read()
    except FileNotFoundError:
        current_readme = "# New Project\n"

    state = extract_state(current_readme)
    config = load_config()
    diff_text = get_git_diff()
    project_tree = get_project_tree()
    
    if "Initial commit" in diff_text or not diff_text.strip():
        print("[AutoReadme] No valid diff found. Skipping generation.")
        sys.exit(0)

    # Compile Prompt
    prompt = f"""
    You are a technical documentation AI. 
    Review the following repository state and generate an updated README.md in raw Markdown.
    
    CURRENT AI STATE SUMMARY:
    {json.dumps(state)}
    
    PROJECT ARCHITECTURE:
    {project_tree}
    
    LATEST GIT DIFF:
    {diff_text}
    
    CURRENT README CONTENT:
    {current_readme}
    
    INSTRUCTIONS:
    1. Update the README content strictly based on the git diff. Do not invent features.
    2. Maintain a highly minimalist and developer-first tone.
    3. You MUST include a new rolling summary at the very bottom of your response, wrapped exactly like this:
       """

    # Dispatch Request
    print("[AutoReadme] Compiling prompt and routing to LLM...")
    new_readme_content = route_llm_payload(prompt, diff_text, config)
    
    if new_readme_content.startswith("API Connection Error") or "Error:" in new_readme_content:
        print(f"[AutoReadme] Generation failed: {new_readme_content}")
        sys.exit(1)

    # Output to File
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme_content)
        
    print("[AutoReadme] README.md successfully updated!")