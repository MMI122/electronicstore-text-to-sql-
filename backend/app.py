from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Import routes
from routes.products import products_bp
from routes.orders import orders_bp
from routes.ai_query import ai_query_bp
from routes.cart import cart_bp
from routes.customers import customers_bp

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gadgets-store-secret-key')
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173", "http://localhost:3001"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Register blueprints
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(ai_query_bp, url_prefix='/api/ai')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')

    @app.route('/')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Gadgets Store API is running',
            'version': '1.0.0'
        })

    @app.route('/api/health')
    def api_health():
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'ai_service': 'available'
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint not found',
            'message': 'The requested URL was not found on the server.'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal server error',
            'message': 'An internal error occurred. Please try again later.'
        }), 500

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad request',
            'message': 'The request could not be understood by the server.'
        }), 400

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🚀 Starting Gadgets Store API on port {port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"🌐 CORS enabled for frontend")
    
    app.run(host='0.0.0.0', port=port, debug=debug)