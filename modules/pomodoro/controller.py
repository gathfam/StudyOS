class PomodoroController:
    def __init__(self, pomodoroService=None, eventBus=None):
        self.pomodoroService = pomodoroService
        self.eventBus = eventBus
        
        # State
        self.workDuration = 25
        self.shortBreakDuration = 5
        self.remainingTime = self.workDuration * 60
        self.isActive = False

    def startTimer(self):
        self.isActive = True
        if self.eventBus and hasattr(self.eventBus, 'emit'):
            self.eventBus.emit('pomodoroStarted')

    def pauseTimer(self):
        self.isActive = False
        if self.eventBus and hasattr(self.eventBus, 'emit'):
            self.eventBus.emit('pomodoroPaused')

    def resetTimer(self):
        self.isActive = False
        self.remainingTime = self.workDuration * 60
        if self.eventBus and hasattr(self.eventBus, 'emit'):
            self.eventBus.emit('pomodoroReset')

    def loadSettings(self):
        if self.pomodoroService and hasattr(self.pomodoroService, 'getSettings'):
            settings = self.pomodoroService.getSettings()
            if settings:
                self.workDuration = settings.get('workDuration', self.workDuration)
                self.shortBreakDuration = settings.get('shortBreakDuration', self.shortBreakDuration)
                if not self.isActive:
                    self.remainingTime = self.workDuration * 60
        else:
            print("Peringatan: pomodoroService belum memiliki fungsi 'getSettings' atau service belum disediakan.")
