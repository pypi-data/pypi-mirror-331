from pathlib import Path

import setuptools

setuptools.setup(
    package_data={
        "challtools": ["challenge.schema.json", "codes.yml"]
        + [
            str(path.relative_to("challtools"))
            for path in Path("challtools/templates").rglob("*")
            if path.is_file()
        ]
    },
)
