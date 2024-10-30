# .github/scripts/wandb_comparator.py

import os
import argparse
import wandb
from ghapi.all import GhApi
import wandb_workspaces.reports as wr

def main():
    # Parse arguments from the command line
    parser = argparse.ArgumentParser(description="Fetch W&B runs and create a comparison report.")
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/repo format")
    parser.add_argument("--pr_number", required=True, type=int, help="Pull request number")
    parser.add_argument("--run_id", required=True, help="ID of the run to compare with baseline")
    parser.add_argument("--token", required=True, help="GitHub token for posting comments")
    args = parser.parse_args()

    # Initialize W&B API and GhApi for GitHub interaction
    wandb_api = wandb.Api()
    gh = GhApi(token=args.token)

    # Split repo argument into owner and name
    repo_owner, repo_name = args.repo.split('/')

    # Fetch the baseline run with tag "baseline"
    try:
        baseline_run = next(
            run for run in wandb_api.runs(path='cicd-quickstart') if 'baseline' in run.tags
        )
    except StopIteration:
        raise ValueError("No baseline run found with the tag 'baseline'.")

    # Fetch the specified comparison run by run_id
    try:
        comparison_run = wandb_api.run(f"cicd-quickstart/{args.run_id}")
    except wandb.errors.CommError:
        raise ValueError(f"No run found with ID {args.run_id}.")

    report = wr.Report(
        entity="bwojcik",
        project="cicd-quickstart",
        title="Baseline comparison",
        description=f"Baseline vs {args.run_id}.",
    )
    pg = wr.PanelGrid(
        runsets=[wr.Runset(entity, project, "Run Comparison").set_filters_with_python_expr(f"ID in ['{run_id}', '{baseline.id}']")],
        panels=[wr.RunComparer(diff_only='split', layout={'w': 24, 'h': 15}),]
    )
    report.blocks = report.blocks[:1] + [pg] + report.blocks[1:]
    report.save()


    # Get the report URL
    report_url = report.url

    # Post a comment on the PR with the report link using ghapi
    gh.issues.create_comment(
        owner=repo_owner,
        repo=repo_name,
        issue_number=args.pr_number,
        body=f"🚀 W&B Comparison Report: [View Report]({report_url})"
    )

if __name__ == "__main__":
    main()
