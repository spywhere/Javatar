from time import clock


class Timer:

    """
    Time counter for measuring speed

    Can be run as single-stage or multi-stage timer
    """

    total_time = 0
    last_timer = clock()

    @staticmethod
    def get_duration():
        """
        Returns time duration since starting the clock
        """
        return clock()-Timer.last_timer

    @staticmethod
    def timer(reset=True):
        """
        Reset the clock to current time and returns time duration since start

        @param reset: a boolean specified whether reset accumulate time duration
            which use in multi-stage timer to zero or not
        """
        duration = Timer.get_duration()
        Timer.last_timer = clock()
        total_time = Timer.total_time + duration
        if reset:
            Timer.total_time = 0
        else:
            Timer.total_time += duration
        return total_time
