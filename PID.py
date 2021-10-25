import time

class PID:
    """PID controller."""

    def init(self, Kp, Ki, Kd, origin_time=None):
        if origin_time is None:
            origin_time = time.time()

        # Gains for each term
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        # Corrections (outputs)
        self.Cp = 0.0
        self.Ci = 0.0
        self.Cd = 0.0

        self.previous_time = origin_time
        self.previous_error = 0.0
        self.gap_count = 0
        



    def Update(self, error, current_time=None):
        
        if current_time is None:
            current_time = time.time()
            
        dt = current_time - self.previous_time
        if dt <= 0.0:
            return 0
        
        de = error - self.previous_error

        self.Cp = error
        self.Ci += error * dt
        self.Cd = de / dt

        self.previous_time = current_time
        self.previous_error = error
        
        output = (self.Kp * self.Cp) + (self.Ki * self.Ci) + (self.Kd * self.Cd) # derivative term
        
        if (output is 0):
            self.gap_count += 1

        return (
            (self.Kp * self.Cp)    # proportional term
            + (self.Ki * self.Ci)  # integral term
            + (self.Kd * self.Cd)  # derivative term
        )

    def gap(self, length):
        return self.gap_count > length
        
        