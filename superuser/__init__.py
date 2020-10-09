# import time, threading
# import schedule

# def job():
#     print("I'm working...")
# def do_something():
#     print('start threading')
#     while True:
#         schedule.every(10).seconds.do(job)
#     print('end threading')
# t = threading.Thread(target=do_something)
# t.start()
# print('Finished all threads')