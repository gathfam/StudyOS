def startup():
    """Inisialisasi sistem core StudyOS saat aplikasi dijalankan."""
    from .database.schema import initializeDatabase
    initializeDatabase()
    
    from .services.activity_service import initializeActivityListeners
    initializeActivityListeners()
    
    print("StudyOS Core initialized successfully.")
