from flask import Flask
from api1 import api1_bp
from api2 import api2_bp
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
CORS(app)

# Register Blueprints
app.register_blueprint(api1_bp, url_prefix="/api1")
app.register_blueprint(api2_bp, url_prefix="/api2")

if __name__ == "__main__":
    app.run(debug=True)
