def startup():
    """Inisialisasi sistem core StudyOS saat aplikasi dijalankan."""
    from .database.schema import initializeDatabase
    initializeDatabase()
    print("StudyOS Core initialized successfully.")
