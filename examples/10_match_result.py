# Result type runtime
class Ok:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"Ok({self.value!r})"

class Err:
    def __init__(self, error):
        self.error = error
    def __repr__(self):
        return f"Err({self.error!r})"

def unwrap_or_else(res, default):
    return ((lambda __match_0: (__match_0.value if isinstance(__match_0, Ok) else default))(res))

def describe_result(res):
    return ((lambda __match_1: ("success" if isinstance(__match_1, Ok) else __match_1.error))(res))

def double_if_ok(res):
    return ((lambda __match_2: ((__match_2.value * 2) if isinstance(__match_2, Ok) else 0))(res))

def handle_parse_result(res):
    return ((lambda __match_3: ((__match_3.value + 1) if isinstance(__match_3, Ok) else (-1)))(res))

def divide(a, b):
    if (b == 0):
        return Err("division by zero")
    return Ok((a / b))

def main():
    success = Ok(42)
    print(unwrap_or_else(success, 0))
    print(describe_result(success))
    failure = Err("something went wrong")
    print(unwrap_or_else(failure, (-1)))
    print(describe_result(failure))
    result1 = divide(10, 2)
    print(double_if_ok(result1))
    result2 = divide(10, 0)
    print(double_if_ok(result2))
    final_value = ((lambda __match_4: (__match_4.value if isinstance(__match_4, Ok) else 0))(divide(100, 4)))
    return print(final_value)


if __name__ == "__main__":
    main()