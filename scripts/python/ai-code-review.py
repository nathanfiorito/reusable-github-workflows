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
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # or "gpt-4" for better quality
MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

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
        return f"""You are an expert code reviewer for a Java Spring Boot application with:
- Java 21
- Spring Boot 3
- PostgreSQL with Row Level Security
- Multi-tenant architecture (Hexagonal)
- JWT authentication
- Flyway migrations

Review the following code changes and provide constructive feedback.

**Focus areas:**
1. **Security**: Authentication, authorization, SQL injection, XSS, secrets exposure
2. **Multi-tenant isolation**: Ensure tenant_id is properly handled
3. **Code quality**: SOLID principles, clean code, naming conventions
4. **Performance**: N+1 queries, inefficient algorithms, missing indexes
5. **Best practices**: Spring Boot conventions, JPA best practices
6. **Testing**: Missing test coverage, edge cases
7. **Documentation**: Missing javadocs, unclear logic

**Changed Files:**
{files_context}

**Instructions:**
- Provide specific, actionable feedback
- Highlight security concerns with 🔴
- Suggest improvements with 💡
- Acknowledge good practices with ✅
- Be concise but thorough
- Focus on critical issues first

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
                        "content": "You are an expert code reviewer specializing in Java Spring Boot applications, security, and clean architecture."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=MAX_TOKENS,
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
- Security vulnerabilities
- Multi-tenant isolation
- Code quality and best practices
- Performance considerations
- Testing coverage

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
