import re
import os

if os.name == 'nt':
    from ._cmd_win import escape_cmd_argument_script as shell_quote  # noqa
else:
    def shell_quote(s):
        return re.sub("(!|\$|#|&|\"|\'|\(|\)|\||<|>|`|\\\|;)", r"\\\1", s)

# win_cmd_escaper
from ._cmd_win import escape_powershell_argument_script as powershell_quote  # noqa
