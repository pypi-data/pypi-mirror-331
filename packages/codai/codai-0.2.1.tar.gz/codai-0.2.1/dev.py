# ruff: noqa
# imports
import json
import codai

from rich import print

from codai.hci import *
from codai.bot import *
from codai.repl import *
from codai.utils import *
from codai.codai import bot

from pydantic_ai.models import KnownModelName

all_models = list(KnownModelName.__args__)

# config
ibis.options.interactive = True
ibis.options.repr.interactive.max_rows = 40
ibis.options.repr.interactive.max_depth = 8
ibis.options.repr.interactive.max_columns = None

# load secrets
load_codai_dotenv()
