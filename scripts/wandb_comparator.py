# .github/scripts/wandb_comparator.py

import os
import argparse
import wandb
from ghapi.all import GhApi

def main():
    # Parse arguments from the command line
    parser = argparse.ArgumentParser(description="Fetch W&B runs and create a comparison report.")
    parser.add_argument("--owner", required=True, help="Owner of the repository")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--pr_number", required=True, type=int, help="Pull request number")
    parser.add_argument("--run_id", required=True, help="ID of the run to compare with baseline")
    args = parser.parse_args()

    # Initialize W&B API and GhApi for GitHub interaction without explicit token
    wandb_api = wandb.Api()
    gh = GhApi(owner=args.owner, repo=args.repo)

    # Fetch the baseline run with tag "baseline"
    try:
        baseline_run = next(
            run for run in wandb_api.runs(path=f"{args.owner}/{args.repo}") if 'baseline' in run.tags
        )
    except StopIteration:
        raise ValueError("No baseline run found with the tag 'baseline'.")

    # Fetch the specified comparison run by run_id
    try:
        comparison_run = wandb_api.run(f"{args.owner}/{args.repo}/{args.run_id}")
    except wandb.errors.CommError:
        raise ValueError(f"No run found with ID {args.run_id}.")

    # Create W&B report comparing the baseline and specified runs
    report = wandb_api.report(
        title=f"Comparison: Baseline vs {args.run_id}",
        description="Automatically generated comparison report",
        blocks=[
            {"type": "runs", "ids": [baseline_run.id, comparison_run.id]},
        ]
    )

    # Get the report URL
    report_url = report.url

    # Post a comment on the PR with the report link using ghapi
    gh.issues.create_comment(
        issue_number=args.pr_number,
        body=f"🚀 W&B Comparison Report: [View Report]({report_url})"
    )

if __name__ == "__main__":
    main()
