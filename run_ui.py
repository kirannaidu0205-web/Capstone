import os
import sys

# Add the project root and frontend/backend to path
root_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_path)
sys.path.append(os.path.join(root_path, 'frontend'))
sys.path.append(os.path.join(root_path, 'backend'))

if __name__ == "__main__":
    print("🚀 Starting Pricing Intelligence Dashboard...")
    from frontend.dashboard.app import app
    app.run(debug=True, port=8050)
