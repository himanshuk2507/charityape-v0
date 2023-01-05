from time import sleep

def smart_ask_worker(args):
    for s in range(3):
        print('My name is Icheka', args)
        sleep(1)
    print('Task completed')
