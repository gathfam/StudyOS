class EventBus:
    def __init__(self):
        self.listeners = {}

    def subscribe(self, eventType, callback):
        """Mendaftarkan callback untuk tipe event tertentu."""
        if eventType not in self.listeners:
            self.listeners[eventType] = []
        self.listeners[eventType].append(callback)

    def unsubscribe(self, eventType, callback):
        """Menghapus callback dari tipe event tertentu."""
        if eventType in self.listeners:
            try:
                self.listeners[eventType].remove(callback)
            except ValueError:
                pass

    def emit(self, eventType, *args, **kwargs):
        """Memicu semua callback yang berlangganan pada eventType."""
        if eventType in self.listeners:
            # Menggunakan salinan list agar aman jika listener memodifikasi subskripsi saat event dipicu
            for callback in list(self.listeners[eventType]):
                callback(*args, **kwargs)

# Menyediakan alias EvenBust untuk kompatibilitas nama kelas jika diperlukan
EvenBust = EventBus

# Singleton instance untuk mempermudah akses global
eventBus = EventBus()

if __name__ == "__main__":
    print("Testing EventBus/EvenBust...")
    
    # Inisialisasi test variables
    testResults = []
    
    # Callback untuk test
    def onTaskCreated(taskTitle, priority="MEDIUM"):
        print(f"Callback received: Task '{taskTitle}' created with priority {priority}")
        testResults.append((taskTitle, priority))
        
    # Test subscribe
    eventBus.subscribe("taskCreated", onTaskCreated)
    print("Subscribed to 'taskCreated' event.")
    
    # Test emit
    eventBus.emit("taskCreated", "Belajar PyQt", priority="HIGH")
    
    # Verifikasi callback dipanggil
    if len(testResults) == 1 and testResults[0] == ("Belajar PyQt", "HIGH"):
        print("EventBus test passed successfully!")
    else:
        print("EventBus test failed.")
        exit(1)
