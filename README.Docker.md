### Building and Running backend

1. **Build Your Docker Image:**

    ```bash
    docker build . --tag backend
    ```

2. **Run Your Docker Image:**

    ```bash
    docker run -p 8080:8080 backend
    ```

    Your application should now be available at:

    ```bash
    http://0.0.0.0:8080
    ```

    If port `8080` is occupied on your machine, you can forward any other available port:

    ```bash
    docker run -p 228:8080 backend
    ```

    Your application will now be accessible at:

    ```bash
    http://0.0.0.0:228
    ```

### Notes

* Ensure Docker is installed and running on your machine.
* Replace `228` with any port number that is available on your machine if `8080` is in use.

### Deploying your application to the cloud

1. First, build your image, e.g.: `docker build -t backend .`.

2. If your cloud uses a different CPU architecture than your development
machine (e.g., you are on a Mac M1 and your cloud provider is amd64),
you'll want to build the image for that platform, e.g.:
`docker build --platform=linux/amd64 -t backend .`.

3. Then, push it to your registry, e.g. `docker push myregistry.com/backend`.


### Notes

* Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/)
docs for more detail on building and pushing.
* [Docker's Python guide](https://docs.docker.com/language/python/)


### Deploying your application to the cloud using the pipeline

Run the `backend_build_and_push` stage in the pipeline.


