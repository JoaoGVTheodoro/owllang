def add(a, b):
    return (a + b)

def greet(name):
    return (("Hello, " + name) + "!")

def is_positive(n):
    return (n > 0)

def main():
    sum = add(10, 20)
    greeting = greet("Owl")
    positive = is_positive(42)
    print(sum)
    print(greeting)
    return print(positive)


if __name__ == "__main__":
    main()