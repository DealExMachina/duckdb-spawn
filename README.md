# DuckDB-SPAWN Data Product

A data product API for project financing using DuckDB, FastAPI, and Prometheus monitoring.

## Table of Contents

- [Features](#features)
- [Local Development](#local-development)
- [Koyeb Deployment](#koyeb-deployment)
- [Monitoring](#monitoring)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Citations](#citations)

## Features

- FastAPI-based REST API
- DuckDB for data storage
- Prometheus metrics collection
- Project financing data model
- Environment-based configuration

## Local Development

1. **Set up the environment**: Ensure you have Docker installed and running on your machine.

2. **Build the Docker image**:

   ```bash
   docker build -t your-image-name .
   ```

3. **Run the Docker container**:

   ```bash
   docker run -p 8000:8000 your-image-name
   ```

4. **Access the application**: Open your browser and go to `http://localhost:8000`.

## Koyeb Deployment

Instructions to deploy the application on Koyeb.

1. **Create a Koyeb account**: If you don't have one, sign up at [Koyeb](https://www.koyeb.com).

2. **Create a new service**:
   - Go to the Koyeb dashboard.
   - Click on "Create Service".
   - Select "Docker" as the deployment method.

3. **Configure the service**:
   - Enter your Docker image name (e.g., `yourusername/yourproject`).
   - Set the port to `8000`.

4. **Deploy the service**:
   - Click "Deploy" to start the deployment process.

5. **Access the application**: Once deployed, Koyeb will provide a URL to access your application.

## Monitoring

Details on how to monitor the application using Prometheus.

## Project Structure

Overview of the project's directory structure and files.

## Contributing

Guidelines for contributing to the project.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

Your Name - [jeanbapt](mailto:jeanbapt@dealexmachina.com)

Project Link: [https://github.com/jeanbapt/duckdb-spawn](https://github.com/jeanbapt/duckdb-spawn)

## Citations

This project utilizes the following technologies:

- **[FastAPI](https://fastapi.tiangolo.com/)**: A modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- **[DuckDB](https://duckdb.org/)**: An in-process SQL OLAP database management system.
- **[Prometheus](https://prometheus.io/)**: An open-source systems monitoring and alerting toolkit.
- **[Koyeb](https://www.koyeb.com/)**: A platform for deploying and running applications in the cloud.
- **[Pulumi](https://www.pulumi.com/)**: A modern infrastructure as code platform that allows you to define cloud resources using programming languages.
