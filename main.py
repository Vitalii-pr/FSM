from fsm import FSM

if __name__ == '__main__':

    fsm = FSM()

    while not fsm.stopped:
        fsm.print_state_options_and_indexes()
        action = input('Enter action to do >>> ')
        fsm.send(action.strip().lower())

    print('You successfully pass 1 day of your life.')