# -*- coding: utf-8 -*-

# For debugging, use this command to start neovim:
#
# NVIM_PYTHON_LOG_FILE=nvim.log NVIM_PYTHON_LOG_LEVEL=DEBUG nvim
#
#
# Please register source before executing any other code, this allow cm_core to
# read basic information about the source without loading the whole module, and
# modules required by this module
import subprocess
from cm import register_source, getLogger, Base

register_source(name='mail',
                abbreviation='mail',
                scopes=['mail'],
                priority=9,
                scoping=True,
                early_cache=True,
                word_pattern=r'[\w/]+',
                cm_refresh_patterns=[r'^(Bcc|Cc|From|Reply-To|To):\s*',
                                     r'^(Bcc|Cc|From|Reply-To|To):.*,\s*'],
                cm_refresh_length=-1)

LOGGER = getLogger(__name__)


class Source(Base):

    def __init__(self, nvim):
        super(Source, self).__init__(nvim)

        # dependency check
        try:
            from distutils.spawn import find_executable
            if not find_executable("lbdbq"):
                self.message('error', 'No lbdbq found.')
        except Exception as ex:
            LOGGER.exception(ex)

    def cm_refresh(self, info, ctx, *args):
        args = ['/usr/local/bin/lbdbq', '.']

        proc = subprocess.Popen(args=args,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        results = proc.communicate('')[0]

        LOGGER.debug("args: %s, result: [%s]", args, results.decode())

        matches = []

        for result in results.decode('utf-8').splitlines():
            try:
                address, name, source = result.strip().split('\t')
                del source
                if name:
                    address = name + ' <' + address + '>'
                    matches.append(address)
            except ValueError:
                pass

        self.complete(info, ctx, ctx['startcol'], matches)
