"""Quran CLI Commands"""

from quran_cli.commands.explore import explore
from quran_cli.commands.export import export
from quran_cli.commands.init import init
from quran_cli.commands.normalize import normalize


# Add your commands here
command_list = [explore, export, init, normalize]
