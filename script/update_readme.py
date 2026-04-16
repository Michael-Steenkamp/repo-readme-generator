import re
import json

def extract_state(readme_text):
    # Parses the current README.md to extract the hidden AI state
    pattern = r'<' + r'!-- AI_STATE_START(.*?)AI_STATE_END --' + r'>'
    
    match = re.search(pattern, readme_text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    
    return {"summary": "New project."}

if __name__ == "__main__":
    # Placeholder for the main execution logic
    print("AutoReadme AI initialized.\n")
