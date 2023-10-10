import itertools
import os
from unittest.mock import patch

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.project.settings")

counter = itertools.count()

# Patch argument name generation for testing.
# Normally function argument names are random, but for testing
# we need predictable names that we can compare against.
with patch("lookup_property.converters.expressions.random_arg_name", side_effect=lambda: f"arg{next(counter)}"):
    django.setup()
