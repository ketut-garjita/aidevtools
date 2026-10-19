# Skill: Deploy to Cloud Run

## Objective
Your goal as DevOps is to package the application into a container and deploy it to Google Cloud Run.

## Instructions
1. **Create a new GCP project** via gcloud command or console
```bash
gcloud projects create aidevtools
```

2. **Link billing**
```bash
gcloud alpha billing projects link [BILLING-ACCOUNT-ID] --project=aidevtools
```

3. **Enable APIs**
```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

4. **Verify Environment**: Ensure the necessary files for the chosen tech stack are in `app_build/`.

5. **Containerize**: Use the IDE terminal to navigate to `app_build/` and run 
```bash
gcloud run deploy --source .
```

6. **Configure**: If prompted by the CLI tool, select your region and allow unauthenticated invocations so the web app is public.

7. **Report**: Output the live production Google Cloud Run URL to the user!
