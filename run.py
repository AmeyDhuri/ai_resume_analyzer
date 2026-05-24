from app import create_app
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)