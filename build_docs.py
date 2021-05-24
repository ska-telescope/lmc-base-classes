import os
from pathlib import Path

rst_contents = """
{header}
{title}
{header}

.. automodule:: {module}
   :members:
"""

paths = [p.relative_to('src') for p in Path('src/ska_tango_base').rglob('*.py')]
for path in paths:
    if path.name == "__init__.py":
        continue

    title = str(path.name)[:-3].replace("_", " ").title().replace("Csp", "CSP")

    module = str(path)[:-3].replace("/", ".")

    target = Path("docs/source/api/", str(path.relative_to('ska_tango_base')).replace(".py", ".rst"))
    target.parent.mkdir(parents=True, exist_ok=True)

    with open(target, 'w') as f:
        f.write(rst_contents.format(
            header="=" * len(title),
            title=title,
            module=module)
        )
