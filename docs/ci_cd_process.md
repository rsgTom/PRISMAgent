# CI/CD Process

This document explains the Continuous Integration and Continuous Deployment setup for the PRISMAgent project.

## Overview

PRISMAgent uses GitHub Actions for automating:
- Code quality checks
- Running tests (unit, integration, end-to-end)
- Building and pushing Docker images
- Deployment to staging and production environments

## Workflow Details

### Code Quality

The [code-quality.yml](../.github/workflows/code-quality.yml) workflow runs on every push to `main` and on pull requests:
- Checks code formatting with Black
- Lints code with Ruff
- Performs type checking with Mypy

### Unit Tests

The [unit-tests.yml](../.github/workflows/unit-tests.yml) workflow:
- Runs pytest on the unit tests directory
- Generates coverage reports
- Uploads coverage data to Codecov

### Integration Tests

The [integration-tests.yml](../.github/workflows/integration-tests.yml) workflow:
- Sets up a Redis service container
- Runs integration tests with the `integration` marker
- Tests interactions between different modules of the application

### End-to-End Tests

The [e2e-tests.yml](../.github/workflows/e2e-tests.yml) workflow:
- Starts all required services using Docker Compose
- Runs tests with the `e2e` marker
- Tests the complete application flow from start to finish

### Deployment

The [deploy.yml](../.github/workflows/deploy.yml) workflow runs on push to `main` and when version tags are created:
- Builds and pushes Docker images to GitHub Container Registry
- Deploys to the staging environment automatically
- Deploys to production after staging deployment is successful and after manual approval

## Pull Request Checks

The [pull-request-checks.yml](../.github/workflows/pull-request-checks.yml) workflow enforces quality standards on pull requests:
- Validates the PR title follows the Conventional Commits format
- Checks for required labels (type and priority)

## Branch Protection Rules

We've configured branch protection rules for the `main` branch:
- Require passing status checks before merging
- Require at least one approval from a code owner
- Prevent pushing directly to `main` (all changes must go through pull requests)

## Setting Up Local Pre-commit Hooks

To ensure your code meets our quality standards locally before pushing, install pre-commit hooks:

```bash
# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

The pre-commit hooks will run the same checks as the CI pipeline on every commit.

## Working with the CI/CD Pipeline

### Creating a New Feature

1. Create a branch from `main`
2. Develop your feature with adequate tests
3. Push your branch and create a PR
4. Address any issues raised by the CI pipeline
5. Get required approvals
6. Merge to `main`

### Creating a Release

1. Merge all desired features into `main`
2. Ensure all tests are passing
3. Create a new tag following semantic versioning: `v1.2.3`
4. The pipeline will automatically build, tag, and deploy the new version

## Environment Configuration

The CI/CD pipeline uses the following environment variables:

- `OPENAI_API_KEY`: Required for tests and deployments (stored in GitHub Secrets)
- `REDIS_HOST` and `REDIS_PORT`: For integration and e2e tests

## Troubleshooting CI/CD Issues

If a workflow fails:

1. Check the GitHub Actions logs for specific error messages
2. For test failures, try to reproduce locally
3. For deployment issues, check the service logs
