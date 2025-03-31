# Document Stream Filter
This is my **Document Stream Filter** web application. The project serves as a practice to familiarize myself with **AWS Cloud**. Here, I experiment with various AWS services and enhance my knowledge of cloud technologies.
The project is deployed on an **AWS EC2 instance** and is public accessible via http://13.48.58.86

## Project Goals
- Utilize and gain hands-on experience with **AWS S3, EC2, ELB, ECS or EKS, DynamoDB, Docker and CI/CD with GitHub Actions**


## Currently Used Technologies
- **Frontend:** Vite
- **Backend:** AWS EC2 (Node.js server)
- **Storage:** AWS S3 (stores the website)
- **Deployment:** EC2 hosting with CI/CD via GitHub Actions

## Installation & Usage

If you want to run the project locally, you can use the provided **Dockerfile**:

1. Clone the repository:
    ```sh
    git clone https://github.com/your-username/document-stream-filter.git
    cd document-stream-filter
    ```

2. Build and start the Docker container:
    ```sh
    docker build -t document-stream-filter .
    docker run -p 3000:3000 document-stream-filter
    ```

This will run the app locally on port 3000, and you can access it at `http://localhost:3000`.

## Future Plans
- Connect **DynamoDB** for storing documents and queries
- Add different document filter written in c++ in a **ECS or EKS**
- Integrate a **ELB** and **auto-scaling** for http traffic

## License

This project is licensed under the **MIT License**.