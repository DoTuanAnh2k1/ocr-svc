from app import create_app
from app.services.ai_model_service import AIModelService
from app.config.settings import Config
import sys


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Server is starting...")
    print("=" * 60)

    # Pre-load AI model
    print("\n📦 Loading AI model (this may take a while)...")
    AIModelService.initialize_model()
    print("✅ Model loaded successfully!\n")
    
    if len(sys.argv) > 1: 
        if sys.argv[1] == 'warmup':
            print("🔥 Warmup complete. Exiting as per 'warmup' argument.")
            sys.exit(0)

    # Create Flask app
    app = create_app()

    print("=" * 60)
    print(f"📍 Healthcheck: http://localhost:{Config.PORT}/healthcheck")
    print(f"📸 Single Image: http://localhost:{Config.PORT}/image-to-text")
    print(f"📂 Folder Batch: http://localhost:{Config.PORT}/extract-from-folder")
    print("=" * 60)
    print("\n🎉 Server is ready to accept requests!\n")

    # Run server
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG, threaded=True)
