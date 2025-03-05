# Transformative

Use AI to write code to convert a type into another type.

## Installation

```bash
pip install transformative
```

Then you can use it like this:

```python
from transformative import init, create

init(generated_code_dir="my/path/for/generated/code/")

circle_to_square = create(Circle, Square)

square = circle_to_square(Circle(radius=1))
```

When the `create` function is called the first time, the project will use an LLM to generate a converter. First, it will
write tests, then it will attempt to write code to pass those tests. If the code passes the tests, it will be saved to
the `generated_code_dir`. Subsequent calls to the `create` function will use the generated code to convert the types.

### Dependencies

This package requires aider-chat to be installed and available on the command line:

```bash
pip install aider-chat
# or
python -m pip install aider-install
```

## Aider

The tool uses `aider` to write the code, calling out to an LLM server based on what API keys are found in your local
environment. More information about configuring aider can be found here: https://aider.chat/docs/config/dotenv.html

## Quick Start

See [src/examples/generate_new_code.py](src/examples/generate_new_code.py) for an example of how to use the tool.

See [notes/master_plan.md](notes/master_plan.md) for plans about future development.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
