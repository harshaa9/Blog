from threading import Thread

def async(func):
  def wrapper(*args, **kwargs):
    thr = Thread(target=func, args=args, kwargs=kwargs)
    thr.start()
  return wrapper