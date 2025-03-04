class HelloWorld:
    def hello_world_english():
        print("Hello World")

    def hello_world_indonesia():
        print("Halo Dunia")

    def hello_world_mandarin():
        print("你好世界")

    def hello_world_korean():
        print("안녕하세요")

def menu():
    print("Please Choose Hello World from 4 Languages")
    print("1. English")
    print("2. Indonesian")
    print("3. Mandarin")
    print("4. Korean")

    choice = int(input("Enter Your Choice: "))

    if choice == 1:
        HelloWorld.hello_world_english()
    elif choice == 2:
        HelloWorld.hello_world_indonesia()
    elif choice == 3:
        HelloWorld.hello_world_mandarin()
    elif choice == 4:
        HelloWorld.hello_world_korean()
    else:
        print("Invalid Choice")

