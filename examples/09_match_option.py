def unwrap_or(opt, default):
    return ((lambda __match_0: (__match_0.value if __match_0 is not None and hasattr(__match_0, 'value') else default))(opt))

def double_or_zero(opt):
    return ((lambda __match_1: ((__match_1.value * 2) if __match_1 is not None and hasattr(__match_1, 'value') else 0))(opt))

def describe_option(opt):
    description = ((lambda __match_2: (__match_2.value if __match_2 is not None and hasattr(__match_2, 'value') else "nothing"))(opt))
    return description

def calculate(opt):
    return ((lambda __match_3: (((__match_3.value + __match_3.value) + 10) if __match_3 is not None and hasattr(__match_3, 'value') else (-1)))(opt))

def main():
    value = Some(42)
    result = unwrap_or(value, 0)
    print(result)
    empty = None
    default_result = unwrap_or(empty, 99)
    print(default_result)
    print(double_or_zero(Some(21)))
    print(double_or_zero(None))
    print(describe_option(Some("hello")))
    return print(describe_option(None))


if __name__ == "__main__":
    main()