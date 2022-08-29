import os
if __name__ == '__main__':
    os.system("locust -f cases/test_locust.py --web-host=127.0.0.1")
