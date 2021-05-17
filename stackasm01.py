# stackasm v0.1
import inspect
import readline
import atexit


def main():
    repl()


def repl():
    load_history()
    print("stackasm v0.1")
    while True:
        try:
            eval_str(input("> "))
        except EvalError as e:
            print(f"eval failed: {e}")
        except EOFError:
            print("bye")
            break


def load_history():
    history_file = ".stackasm_history"
    try:
        readline.read_history_file(history_file)
    except FileNotFoundError:
        try:
            with open(history_file, "wb"):
                pass
        except IOError as e:
            print(f"failed to create history file {history_file}")
            sys.exit(1)

    atexit.register(readline.write_history_file, history_file)


def eval_str(source: str):
    for word in source.split():
        evaluate(word)


# evaluator state
stack = []
dictionary = {}


class EvalError(Exception):
    """Evaluation failed"""


current_quote = []
quote_depth = 0


def evaluate(word: str):
    global current_quote, quote_depth
    if word == "]":
        quote_depth -= 1
        if quote_depth == 0:
            stack.append(current_quote)
        else:
            current_quote.append(word)
        return
    if word == "[":
        if quote_depth == 0:
            current_quote = []
        else:
            current_quote.append(word)
        quote_depth += 1
        return
    if quote_depth:
        current_quote.append(word)
        return
    if isinstance(word, str) and word.startswith("'"):
        stack.append(word[1:])
        return
    if isinstance(word, list):
        stack.append(word)
        return
    try:
        stack.append(int(word))
        return
    except ValueError:
        pass
    try:
        fn = dictionary[word]
    except KeyError:
        raise EvalError(f"unknown word: {word}") from None
    fn()


# builtins
def builtin(name_or_fn):
    if isinstance(name_or_fn, str):
        def inner(fn):
            if not callable(fn):
                raise ValueError("expected a function")
            dictionary[name_or_fn] = lambda: stack_call(fn)
            return fn
        return inner
    if callable(name_or_fn):
        dictionary[name_or_fn.__name__] = lambda: stack_call(name_or_fn)
        return name_or_fn
    else:
        raise ValueError("expected a function or a name")


def stack_call(fn):
    global stack
    if not callable(fn):
        raise ValueError("expected a callable")
    arity = len(inspect.signature(fn).parameters)
    if arity > len(stack):
        raise EvalError("stack underflow")
    if arity > 0:
        args = stack[-arity:]
        stack = stack[:-arity]
    else:
        args = []
    result = fn(*args)
    if result is None:
        return
    if isinstance(result, tuple):
        stack.extend(result)
    else:
        stack.append(result)


def stack_pretty(l):
    def pretty_parts(l):
        for item in l:
            if isinstance(item, list):
                yield "["
                yield from pretty_parts(item)
                yield "]"
            else:
                yield str(item)
    return " ".join(pretty_parts(l))


@builtin
def apply(quotation):
    for word in quotation:
        evaluate(word)


@builtin("def")
def define(name, value):
    if isinstance(value, list):
        dictionary[name] = lambda: apply(value)
    else:
        dictionary[name] = lambda: stack.append(value)


@builtin("+")
def add(a, b):
    return a + b


@builtin
def drop(x):
    return


@builtin
def swap(x, y):
    return y, x


@builtin
def dup(x):
    return x, x


@builtin("shift-left")
def shift_left(x, amount):
    return x << amount

@builtin("shift-right")
def shift_right(x, amount):
    return x >> amount


@builtin("bitwise-or")
def bitwise_or(x, y):
    return x | y


@builtin("import")
def import_file(name):
    with open(name, "r") as f:
        source = f.read()
    eval_str(source)


@builtin("bin")
def make_bin(x):
    # hax
    return int(str(x), 2)


@builtin(".")
def print_top_of_stack(x):
    print(x)


@builtin(".s")
def print_stack():
    print(f"stack: {stack_pretty(stack)}")


current_buffer = []


builtin("emit")(lambda x: current_buffer.append(x & 0xFF))


@builtin("print-buffer")
def print_buffer():
    print(current_buffer)


@builtin("bin-buffer")
def bin_buffer():
    for item in current_buffer:
        print(bin(item)[2:].rjust(8, "0"))


@builtin("buffer-pos")
def buffer_pos():
    return len(current_buffer)


builtin("clear-buffer")(current_buffer.clear)


if __name__ == "__main__":
    main()

