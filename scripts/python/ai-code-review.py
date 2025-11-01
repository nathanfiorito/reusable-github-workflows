#!/usr/bin/env python3
"""
AI Code Review Script using OpenAI API
Analyzes pull request changes and provides intelligent code review feedback.
"""

import os
import sys
import json
import re
from typing import List, Dict, Any
from github import Github
from openai import OpenAI

# Configuration
MODEL = os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07")  # or "gpt-4" for better quality
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
def get_temperature() -> float:
    """Return a temperature compatible with current model constraints."""
    raw = os.getenv("OPENAI_TEMPERATURE", "1").strip()
    try:
        value = float(raw)
    except ValueError:
        print(f"⚠️ Invalid OPENAI_TEMPERATURE '{raw}'. Defaulting to 1.0")
        return 1.0

    if value != 1.0:
        print(f"ℹ️ OPENAI_TEMPERATURE {value} unsupported for this model. Using 1.0 instead.")
        return 1.0

    return value

TEMPERATURE = get_temperature()

# File size limits (to avoid token overflow)
MAX_FILE_SIZE = int(os.getenv("AI_REVIEW_MAX_FILE_SIZE", "10000"))  # characters
MAX_FILES_TO_REVIEW = int(os.getenv("AI_REVIEW_MAX_FILES", "20"))


class CodeReviewer:
    def __init__(self):
        self.openai_api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not self.openai_api_key:
            print("❌ OPENAI_API_KEY not found. Skipping AI review.")
            sys.exit(0)

        self.github_token = (os.getenv("GITHUB_TOKEN") or "").strip()
        if not self.github_token:
            print("❌ GITHUB_TOKEN not found. Cannot authenticate with GitHub API.")
            sys.exit(1)

        pr_number_env = (os.getenv("PR_NUMBER") or "").strip()
        if not pr_number_env:
            print("❌ PR_NUMBER not provided. Pass the pull request number via workflow inputs.")
            sys.exit(1)

        try:
            self.pr_number = int(pr_number_env)
        except ValueError:
            print(f"❌ Invalid PR_NUMBER value: {pr_number_env}")
            sys.exit(1)

        self.repo_name = (os.getenv("REPO_NAME") or os.getenv("GITHUB_REPOSITORY") or "").strip()
        if not self.repo_name:
            print("❌ REPO_NAME not provided and GITHUB_REPOSITORY unavailable.")
            sys.exit(1)

        self.openai_client = OpenAI(api_key=self.openai_api_key)
        self.github_client = Github(self.github_token)
        self.repo = self.github_client.get_repo(self.repo_name)
        self.pr = self.repo.get_pull(self.pr_number)

        print(f"🔍 Reviewing PR #{self.pr_number}: {self.pr.title}")

    def get_changed_files(self) -> List[Any]:
        """Get list of changed files in the PR."""
        files = list(self.pr.get_files())
        print(f"📁 Found {len(files)} changed file(s)")
        return files[:MAX_FILES_TO_REVIEW]

    def should_review_file(self, file) -> bool:
        """Determine if file should be reviewed."""
        # Skip deleted files
        if file.status == 'removed':
            return False

        # Review specific file types
        reviewable_extensions = [
            '.java', '.yml', '.yaml', '.xml', '.sql',
            '.properties', '.json', '.sh', '.py'
        ]

        return any(file.filename.endswith(ext) for ext in reviewable_extensions)

    def get_file_context(self, file) -> str:
        """Get file context for review."""
        context = f"### File: {file.filename}\n"
        context += f"**Status**: {file.status}\n"
        context += f"**Changes**: +{file.additions} -{file.deletions}\n\n"

        if file.patch and len(file.patch) < MAX_FILE_SIZE:
            context += "**Diff:**\n```diff\n"
            context += file.patch
            context += "\n```\n"
        else:
            context += "*File too large for detailed review*\n"

        return context

    def create_review_prompt(self, files_context: str) -> str:
        """Create the prompt for OpenAI."""
        return f"""You are an expert software engineer and code reviewer with deep experience across multiple programming languages, frameworks, and architectural styles. Review the following code changes and provide constructive, context-aware feedback.

**Focus areas:**
1. **Correctness**: Logic errors, data handling, edge cases, cross-file implications
2. **Security**: Authentication, authorization, data exposure, injection risks, secret handling
3. **Maintainability**: Readability, consistency, abstractions, code smells, dead code
4. **Performance**: Inefficient algorithms, unnecessary complexity, resource usage, scalability
5. **Testing**: Missing or insufficient automated tests, edge case coverage, reliability
6. **Documentation & DX**: Comments, README/docs updates, configuration clarity, migration steps
7. **Dependencies & Tooling**: Versioning impacts, build scripts, CI/CD implications

**Changed Files:**
{files_context}

**Instructions:**
- Provide specific, actionable feedback tailored to the language or framework in each file
- Highlight critical or high-risk issues with 🔴
- Suggest improvements or alternatives with 💡
- Recognize strong patterns or best practices with ✅
- Be concise but thorough; prioritize the most impactful findings
- When you flag an issue, follow this structure and always include concrete code snippets:
  ---
  # <file or class name>
  ---
  ## <short imperative summary of the change needed>
  Flagged snippet:
  ```<language>
  <current/problematic code>
  ```
  Suggested fix:
  ```<language>
  <proposed fix>
  ```
- Use the appropriate language identifier in fenced code blocks; if unknown, omit the identifier but still provide the snippet
- If the code snippet is unavailable, describe the snippet needed and provide a plausible fix in code form

Provide your review in Markdown format.
"""

    def review_with_openai(self, prompt: str) -> str:
        """Send prompt to OpenAI and get review."""
        print("🤖 Sending to OpenAI for review...")

        try:
            response = self.openai_client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer proficient across multiple programming languages, frameworks, and architectures, with deep knowledge of security, reliability, and maintainability best practices. Present each finding using the mandated structure that includes the file or class name, a concise summary, the problematic snippet, and a suggested fix, all formatted with Markdown code fences."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_completion_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            review = response.choices[0].message.content
            print(f"✅ Review completed ({response.usage.total_tokens} tokens used)")
            return review

        except Exception as e:
            print(f"❌ OpenAI API error: {e}")
            return f"⚠️ Failed to complete AI review: {str(e)}"

    def format_review_summary(self, review: str, files_count: int) -> str:
        """Format the final review summary."""
        summary = f"""## 🤖 AI Code Review

**Powered by:** OpenAI {MODEL}
**Files reviewed:** {files_count}
**PR:** #{self.pr_number} - {self.pr.title}

---

{review}

---

<details>
<summary>ℹ️ About this review</summary>

This automated code review was generated using OpenAI's {MODEL} model.
The review focuses on:
- Security vulnerabilities and secret handling
- Correctness and reliability
- Code quality and maintainability best practices
- Performance and scalability considerations
- Testing coverage and validation
- Documentation and developer experience impacts

**Note:** This is an automated review. Please use your judgment and verify suggestions before applying them.

</details>

*Review generated at: {self.get_timestamp()}*
"""
        return summary

    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    def save_review(self, summary: str, details: Dict):
        """Save review to files."""
        # Save markdown summary
        with open('review-summary.md', 'w', encoding='utf-8') as f:
            f.write(summary)

        # Save JSON details
        with open('review-details.json', 'w', encoding='utf-8') as f:
            json.dump(details, f, indent=2)

        print("💾 Review saved to files")

    def run(self):
        """Main execution flow."""
        try:
            # Get changed files
            files = self.get_changed_files()

            if not files:
                print("ℹ️ No files to review")
                return

            # Filter reviewable files
            reviewable_files = [f for f in files if self.should_review_file(f)]

            if not reviewable_files:
                print("ℹ️ No reviewable files found")
                return

            print(f"📝 Reviewing {len(reviewable_files)} file(s)...")

            # Build context
            files_context = "\n\n".join(
                self.get_file_context(f) for f in reviewable_files
            )

            # Create prompt
            prompt = self.create_review_prompt(files_context)

            # Get review from OpenAI
            review = self.review_with_openai(prompt)

            # Format summary
            summary = self.format_review_summary(review, len(reviewable_files))

            # Save results
            details = {
                "pr_number": self.pr_number,
                "pr_title": self.pr.title,
                "files_reviewed": len(reviewable_files),
                "model": MODEL,
                "timestamp": self.get_timestamp(),
                "files": [f.filename for f in reviewable_files]
            }

            self.save_review(summary, details)

            print("✅ Code review completed successfully!")

        except Exception as e:
            print(f"❌ Error during review: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    reviewer = CodeReviewer()
    reviewer.run()
