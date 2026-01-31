import math

def add(a, b):
    return (a + b)

def greet(name):
    print((("Hello, " + name) + "!"))

def main():
    x = 10
    y = 20
    pi = 3.14159
    message = "OwlLang MVP"
    is_ready = True
    sum = (x + y)
    product = (x * y)
    difference = (y - x)
    print("=== OwlLang MVP Demo ===")
    print(message)
    print(sum)
    print(product)
    result = add(100, 200)
    print(result)
    sqrt_result = math.sqrt(16.0)
    print(sqrt_result)
    ceil_result = math.ceil(3.2)
    print(ceil_result)
    greet("World")
    print("=== Done! ===")


if __name__ == "__main__":
    main()