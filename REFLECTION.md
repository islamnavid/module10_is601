# Module 10 Reflection

**Name:** Md Navidul Islam
**Course:** IS601 — Python for Web API Development
**Assignment:** Module 10 — Secure User Model, Pydantic Validation, Database Testing, and Docker Deployment

## Overview

In Module 10, I worked on enhancing my FastAPI application with secure user management, database integration, automated testing, and Docker deployment. The assignment helped me understand how different technologies work together to create a secure and reliable backend application.

## Secure User Model and Validation

One of the important parts of this assignment was implementing secure user data handling using SQLAlchemy and Pydantic. I learned how database models define the structure of stored information, while Pydantic schemas validate incoming data and control which information is returned to users.

Password security was another important concept. Instead of storing plain-text passwords, the application uses password hashing. This helped me understand why sensitive information must be protected and how password verification works.

## Testing and Database Integration

I worked with automated tests to verify the application's functionality. Unit tests helped check individual components, while integration tests helped verify how the application interacts with PostgreSQL.

I also used GitHub Actions to automate testing. This demonstrated how continuous integration can detect problems whenever code changes are pushed to GitHub.

## Challenges Faced

The most challenging part of this assignment was configuring the Docker image and CI/CD pipeline.

Initially, the Docker build encountered dependency compatibility problems involving the Python version. I addressed this by updating the Docker configuration to use Python 3.11.

Another challenge involved security vulnerabilities reported by Trivy. I investigated the installed package versions, examined the Docker image, and discovered that outdated package information in pip's bundled metadata was contributing to a security scan finding. After updating the Docker configuration, the security job passed.

I also experienced Docker Hub authentication and authorization errors during deployment. The first issue involved missing GitHub Actions secrets. After configuring the Docker Hub username and access token, I encountered another error because the token did not have sufficient repository permissions. Creating a token with read and write permissions resolved the problem.

## Final Results

After troubleshooting, all three GitHub Actions jobs completed successfully:

- Test — Passed
- Security — Passed
- Deploy — Passed

The Docker image was successfully published to Docker Hub.

## What I Learned

This assignment strengthened my understanding of secure backend development, automated testing, Docker containerization, and CI/CD pipelines.

I also learned the importance of carefully reading error messages, investigating dependency vulnerabilities, managing secrets securely, and verifying each stage of the deployment process.

The experience helped me become more comfortable with real-world development workflows and prepared me to continue building on this FastAPI project in future modules.

## Project Links

**GitHub:** [https://github.com/islamnavid/module10_is601](https://github.com/islamnavid/module10_is601)

**Docker Hub:** [https://hub.docker.com/r/navidislam/module10_is601](https://hub.docker.com/r/navidislam/module10_is601)
