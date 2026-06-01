class PomodoroHandlers:
    def __init__(self, controller):
        self.controller = controller

    def handleStartClick(self):
        self.controller.startTimer()

    def handlePauseClick(self):
        self.controller.pauseTimer()

    def handleResetClick(self):
        self.controller.resetTimer()
