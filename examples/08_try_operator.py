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

def parse_number(s):
    if (s == "42"):
        return Ok(42)
    else:
        return Err("not a valid number")

def double_parsed(s):
    __try_0 = parse_number(s)
    if isinstance(__try_0, Err):
        return __try_0
    n = __try_0.value
    return Ok((n * 2))

def main():
    result1 = double_parsed("42")
    result2 = double_parsed("abc")
    print(result1)
    print(result2)


if __name__ == "__main__":
    main()