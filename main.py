from src.app_factory import create_app

app = create_app()

@app.cli.command("cleanup-rooms")
def cleanup_rooms_command():
    from src.services.room_service import room_service
    count = room_service.cleanup_stale_rooms()
    print(f"Successfully cleaned up {count} rooms.")

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
