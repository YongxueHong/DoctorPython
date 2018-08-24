class DoctorError(Exception):
    def __init__(self, err):
        self.error_info = err
    def __str__(self):
        return self.error_info