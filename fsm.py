import random

state_indexes = {
    'sleep': {'time': 60, 'fresh_index': -0.05, 'productivity_index': -0.03, 'appetite_index': 0.02, 'sleepy_index': -0.1},
    'wake_up': {'time': 15, 'fresh_index': 0, 'productivity_index': 0.01, 'appetite_index': 0, 'sleepy_index': 0.01},
    'meal_time': {'time': 30, 'fresh_index': -0.02, 'productivity_index': 0.00, 'appetite_index': -1, 'sleepy_index': 0.02},
    'chill': {'time': 20, 'fresh_index': -0.04, 'productivity_index': -0.05, 'appetite_index': 0.02, 'sleepy_index': 0.02},
    'workout': {'time': 60, 'fresh_index': -0.2, 'productivity_index': 0.05, 'appetite_index': 0.05, 'sleepy_index': 0.2},
    'take_shower': {'time': 20, 'fresh_index': 1, 'productivity_index': 0.00, 'appetite_index': 0.02, 'sleepy_index': 0.02},
    'reading': {'time': 60, 'fresh_index': -0.04, 'productivity_index': 0.07, 'appetite_index': 0.05, 'sleepy_index': 0.07},
    'study': {'time': 60, 'fresh_index': -0.04, 'productivity_index': 0.1, 'appetite_index': 0.05, 'sleepy_index': 0.07},
}

states_ways = {
    'sleep': {'wake_up', 'sleep'},
    'wake_up': {'sleep', 'meal_time', 'take_shower'},
    'meal_time': {'chill', 'study'},
    'chill': {'workout', 'meal_time', 'chill', 'study', 'reading'},
    'study': {'workout', 'study', 'chill'},
    'take_shower': {'meal_time', 'reading', 'sleep'},
    'reading': {'take_shower', 'study', 'sleep', 'reading'},
    'workout': {'take_shower', 'chill', 'study', 'reading'},
}


def prime(fn):
    def wrapper(*args, **kwargs):
        v = fn(*args, **kwargs)
        v.send(None)
        return v
    return wrapper


class FSM:
    def __init__(self):
        self.fresh_index: float = random.random().__round__(2)
        self.productivity_index: float = random.random().__round__(2)
        self.appetite_index: float = random.random().__round__(2)
        self.sleepy_index: float = random.random().__round__(2)

        self.time = 420
        self.indexes = [self.fresh_index, self.productivity_index, self.appetite_index, self.sleepy_index]

        self.sleep = self._sleep_state()
        self.wake_up = self._wake_up_state()
        self.meal_time = self._meal_time_state()
        self.chill = self._chill_state()
        self.workout = self._workout_state()
        self.reading = self._reading_state()
        self.study = self._study_state()
        self.take_shower = self._take_shower_state()


        self.current_state = self.sleep
        self.state = 'sleep'

        self.stopped = False

    def send(self, action):
        """The function sends the current input to the current state
        It captures the StopIteration exception and marks the stopped flag.
        """
        try:
            self.current_state.send(action)
        except StopIteration:
            self.stopped = True

    def change_indexes(self, state):
        self.fresh_index = max(0, min(1, self.fresh_index + state_indexes[state]['fresh_index']))
        self.productivity_index = max(0, min(1, self.productivity_index + state_indexes[state]['productivity_index']))
        self.appetite_index = max(0, min(1, self.appetite_index + state_indexes[state]['appetite_index']))
        self.sleepy_index = max(0, min(1, self.sleepy_index + state_indexes[state]['sleepy_index']))
        self.time += state_indexes[state]['time']
        if self.time >= 1440:
            self.time = 0
            self.stopped = True

        self.state = state

    def print_state_options_and_indexes(self):
        print(f'''
        Time: {self.time//60}hr {self.time%60}min
        ---------
        Current state: {self.state}
        ---------
        Fresh index: {self.fresh_index.__round__(2)}
        Productivity index: {self.productivity_index.__round__(2)}
        Appetite index: {self.appetite_index.__round__(2)}
        Sleepy index: {self.sleepy_index.__round__(2)}
        ---------
        Enter state to do {self.current_options()}
        ---------
        ''')

    def current_options(self):
        options: set = states_ways[self.state]
        if self.state == 'sleep':
            options = options - {'sleep'} if self.sleepy_index < 0.1 else options
            return options
        if self.state == 'workout':
            return {'take_shower'}
        options: set = states_ways[self.state]
        options.add('take_shower' if self.fresh_index < 0.2 else None)

        options.add('sleep' if self.sleepy_index > 0.1 else None)
        options = options - {'sleep'} if self.sleepy_index < 0.6 else options
        options = options - {'meal_time'} if self.appetite_index < 0.4 else options

        return options - {None}

    @prime
    def _sleep_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'wake_up' and action in actions:
                self.change_indexes('wake_up')
                self.current_state = self._wake_up_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            else:
                print("Invalid action. Try again.")

    @prime
    def _wake_up_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            elif action == 'meal_time' and action in actions:
                self.change_indexes('meal_time')
                self.current_state = self._meal_time_state()
            elif action == 'take_shower' and action in actions:
                self.change_indexes('take_shower')
                self.current_state = self._take_shower_state()
            else:
                print("Invalid action. Try again.")

    @prime
    def _take_shower_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'meal_time' and action in actions:
                self.change_indexes('meal_time')
                self.current_state = self._meal_time_state()
            elif action == 'reading' and action in actions:
                self.change_indexes('reading')
                self.current_state = self._reading_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            else:
                print("Invalid action. Try again.")


    @prime
    def _meal_time_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'chill' and action in actions:
                self.change_indexes('chill')
                self.current_state = self._chill_state()
            elif action == 'study' and action in actions:
                self.change_indexes('study')
                self.current_state = self._study_state()
            elif action == 'take_shower' and action in actions:
                self.change_indexes('take_shower')
                self.current_state = self._take_shower_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            else:
                print("Invalid action. Try again.")


    @prime
    def _chill_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'chill' and action in actions:
                self.change_indexes('chill')
                self.current_state = self._chill_state()
            elif action == 'workout' and action in actions:
                self.change_indexes('workout')
                self.current_state = self._workout_state()
            elif action == 'meal_time' and action in actions:
                self.change_indexes('meal_time')
                self.current_state = self._meal_time_state()
            elif action == 'take_shower' and action in actions:
                self.change_indexes('take_shower')
                self.current_state = self._take_shower_state()
            elif action == 'study' and action in actions:
                self.change_indexes('study')
                self.current_state = self._study_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            else:
                print("Invalid action. Try again.")

    @prime
    def _study_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'workout' and action in actions:
                self.change_indexes('workout')
                self.current_state = self._workout_state()
            elif action == 'study' and action in actions:
                self.change_indexes('study')
                self.current_state = self._study_state()
            elif action == 'chill' and action in actions:
                self.change_indexes('chill')
                self.current_state = self._chill_state()
            elif action == 'take_shower' and action in actions:
                self.change_indexes('take_shower')
                self.current_state = self._take_shower_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            else:
                print("Invalid action. Try again.")

    @prime
    def _workout_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'take_shower' and action in actions:
                self.change_indexes('take_shower')
                self.current_state = self._take_shower_state()
            elif action == 'chill' and action in actions:
                self.change_indexes('chill')
                self.current_state = self._chill_state()
            elif action == 'study' and action in actions:
                self.change_indexes('study')
                self.current_state = self._study_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            else:
                print("Invalid action. Try again.")


    @prime
    def _reading_state(self):
        while True:
            action = yield
            actions = self.current_options()
            if action == 'take_shower' and action in actions:
                self.change_indexes('take_shower')
                self.current_state = self._take_shower_state()
            elif action == 'chill' and action in actions:
                self.change_indexes('chill')
                self.current_state = self._chill_state()
            elif action == 'study' and action in actions:
                self.change_indexes('study')
                self.current_state = self._study_state()
            elif action == 'sleep' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._sleep_state()
            elif action == 'reading' and action in actions:
                self.change_indexes('sleep')
                self.current_state = self._reading_state()
            else:
                print("Invalid action. Try again.")
