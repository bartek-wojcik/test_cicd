
import os
import wandb
from ghapi.all import GhApi

def main():
    # Initialize W&B API and GhApi for GitHub interaction
    wandb_api = wandb.Api()
    gh = GhApi(token=os.getenv('GITHUB_TOKEN'))

    # Extract environment variables
    run_id = os.getenv('RUN_ID')
    repo = os.getenv('REPO')
    pr_number = os.getenv('PR_NUMBER')
    repo_owner, repo_name = repo.split('/')

    # Fetch the baseline run with tag "baseline"
    try:
        baseline_run = next(
            run for run in wandb_api.runs(path=repo) if 'baseline' in run.tags
        )
    except StopIteration:
        raise ValueError("No baseline run found with the tag 'baseline'.")

    # Fetch the specified comparison run by run_id
    try:
        comparison_run = wandb_api.run(f"{repo}/{run_id}")
    except wandb.errors.CommError:
        raise ValueError(f"No run found with ID {run_id}.")

    # Create W&B report comparing the baseline and specified runs
    report = wandb_api.report(
        title=f"Comparison: Baseline vs {run_id}",
        description="Automatically generated comparison report",
        blocks=[
            {"type": "runs", "ids": [baseline_run.id, comparison_run.id]},
        ]
    )

    # Get the report URL
    report_url = report.url

    # Post a comment on the PR with the report link using ghapi
    gh.issues.create_comment(
        owner=repo_owner,
        repo=repo_name,
        issue_number=int(pr_number),
        body=f"🚀 W&B Comparison Report: [View Report]({report_url})"
    )

if __name__ == "__main__":
    main()
