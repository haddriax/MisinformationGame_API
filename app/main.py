import argparse

from fast_api_application import FastAPIWrapper

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Run the The Misinformation Game backend"
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    args = parser.parse_args()

    api_app = FastAPIWrapper(development_mode=args.debug)
    api_app.run(host="127.0.0.1" if args.debug else "0.0.0.0", port=8080)
