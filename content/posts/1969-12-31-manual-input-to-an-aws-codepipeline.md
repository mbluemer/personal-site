---
title: Manual Parameterized Deploys with AWS CodePipeline
slug: manual-input-to-an-aws-codepipeline
date: 1970-01-01T00:00:00.000Z
draft: true
---

- [https://docs.gitlab.com/ee/ci/pipelines/#run-a-pipeline-manually](https://docs.gitlab.com/ee/ci/pipelines/#run-a-pipeline-manually)
- [https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/](https://www.jenkins.io/doc/pipeline/steps/pipeline-input-step/)

### Problem

We want to be able to run an AWS CodePipeline with a particular manual input parameter to control what we're deploying. In this case I'm going to demonstrate 

The use case I'm looking to implement is a manual deploy where the user can specify a particular parameter that we're basing the deployment off of. In this case we bake AMIs with new code changes that are then deployed so I want to give developers the ability to specify what AMI they want to deploy in this pipeline.

The decided route was to create a pipeline that's only every run manually which pulls a parameter from SSM Parameter Store and runs the pipeline based on that, with a verification step to double check that the desired AMI is in fact the one that's going to be deployed.

### Gotchas

- Pipeline Executions persist
- Requires manual input
