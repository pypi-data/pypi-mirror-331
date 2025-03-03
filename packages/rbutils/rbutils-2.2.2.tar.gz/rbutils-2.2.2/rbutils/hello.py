def helloworld():
    print("hello robin")


class HelloCount:
    cnt = 0

    def count(self):
        self.cnt += 1

    def hello(self):
        print(f"hello,now count is:{self.cnt}")


class Hello:
    name = None

    def __init__(self, name):
        self.name = name

    def hello(self):
        print(f"hello,i am {self.name}")


if __name__ == "__main__":
    helloworld()
