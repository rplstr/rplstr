#!/usr/bin/env python3
"""
GitHub Language Stats CLI Generator
"""

import os
import requests
import base64
from github import Github
from collections import Counter
import math


GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME")
README_REPO = os.environ.get("README_REPO", GITHUB_USERNAME)  
MAX_LANGUAGES = 10  
MIN_PERCENTAGE = 1.0  
BAR_LENGTH = 20  


FULL_BLOCK = "█"
EMPTY_BLOCK = "░"

def fetch_language_stats():
    """Fetch language statistics from GitHub API"""
    if not GITHUB_TOKEN:
        raise ValueError("GitHub token not found. Set the GITHUB_TOKEN environment variable.")
    
    if not GITHUB_USERNAME:
        raise ValueError("GitHub username not found. Set the GITHUB_USERNAME environment variable.")
    
    g = Github(GITHUB_TOKEN)
    user = g.get_user(GITHUB_USERNAME)
    
    
    repos = user.get_repos()
    
    
    language_bytes = Counter()
    
    for repo in repos:
        if repo.fork:  
            continue
        
        languages = repo.get_languages()
        for language, bytes_count in languages.items():
            language_bytes[language] += bytes_count
    
    
    total_bytes = sum(language_bytes.values())
    if total_bytes == 0:
        return []
    
    language_percentages = [
        (language, count, (count / total_bytes) * 100)
        for language, count in language_bytes.items()
    ]
    
    
    language_percentages.sort(key=lambda x: x[2], reverse=True)
    
    
    language_percentages = [
        lang for lang in language_percentages if lang[2] >= MIN_PERCENTAGE
    ]
    
    
    return language_percentages[:MAX_LANGUAGES]

def generate_cli_bar(percentage):
    """Generate a CLI-style bar using Unicode block characters"""
    filled_blocks = math.floor(percentage / 100 * BAR_LENGTH)
    empty_blocks = BAR_LENGTH - filled_blocks
    
    return FULL_BLOCK * filled_blocks + EMPTY_BLOCK * empty_blocks

def generate_language_stats_markdown(language_stats):
    """Generate markdown for language statistics"""
    if not language_stats:
        return "No language statistics available."
    
    
    max_language_length = max(len(lang[0]) for lang in language_stats)
    
    
    output = ""
    
    for language, bytes_count, percentage in language_stats:
        
        padded_language = language.ljust(max_language_length)
        
        
        bar = generate_cli_bar(percentage)
        
        
        formatted_percentage = f"{percentage:.1f}%"
        
        
        output += f"{padded_language}  {bar}  {formatted_percentage}\n"
    
    output += ""
    
    return output

def update_github_readme(content):
    """Update GitHub profile README with the generated content"""
    if not GITHUB_TOKEN:
        raise ValueError("GitHub token not found. Set the GITHUB_TOKEN environment variable.")
    
    if not README_REPO:
        raise ValueError("README repository not specified.")
    
    g = Github(GITHUB_TOKEN)
    
    
    repo = g.get_repo(README_REPO)
    
    try:
        
        readme = repo.get_contents("README.md")
        current_content = base64.b64decode(readme.content).decode("utf-8")
        
        
        start_marker = "<!-- GITHUB_LANGUAGE_STATS_START -->"
        end_marker = "<!-- GITHUB_LANGUAGE_STATS_END -->"
        
        if start_marker in current_content and end_marker in current_content:
            
            start_idx = current_content.find(start_marker)
            end_idx = current_content.find(end_marker) + len(end_marker)
            
            new_content = (
                current_content[:start_idx] + 
                start_marker + "\n" + content + "\n" + 
                end_marker + 
                current_content[end_idx:]
            )
        else:
            
            new_content = current_content + "\n\n" + start_marker + "\n" + content + "\n" + end_marker
        
        
        repo.update_file(
            path="README.md",
            message="Update language statistics",
            content=new_content,
            sha=readme.sha
        )
        
        print("GitHub profile README updated successfully!")
        
    except Exception as e:
        print(f"Error updating README: {e}")
        raise

def main():
    """Main function"""
    try:
        print("Fetching...")
        language_stats = fetch_language_stats()
        
        print("Generating...")
        markdown_content = generate_language_stats_markdown(language_stats)
        
        print("Updating...")
        update_github_readme(markdown_content)
        
        print("OK.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 
