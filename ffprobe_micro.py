"""
source: https://stackoverflow.com/a/63215561/10681595
"""

import subprocess
import json
from pathlib import Path
import logging


class FFProbeResult:

    def __init__(self, return_code: int = None, output: str = '', error: str = '', format=None):
        self.return_code = return_code
        self.output = output
        self.error = error
        self.format = format
        self._output_as_dict = None

    def get_output_as_dict(self):
        if self._output_as_dict is None:
            if self.format == 'json':
                self._output_as_dict = json.loads(self.output)
            elif self.format == 'flat':
                output = [e.split('=') for e in self.output.strip().split('\n')]
                self._output_as_dict = {key_val[0]: key_val[1] for key_val in output}
            else:
                raise ValueError("ffprobe format '%s' not supported to build dict" % self.format)
        return self._output_as_dict

    def to_json_file(self, path: Path, mode='w', **kwargs):
        """
        :param mode: file open mode
        :param kwargs: kwargs for pathlib.Path().open()
        """
        path = path if isinstance(path, Path) else Path(path)
        with path.open(mode, **kwargs) as f:
            json.dump(self.get_output_as_dict(), f, indent=4)
            logging.debug('Dumped ffprobe output into %s', path)


def ffprobe(file_path, ffprobe_format="json", format_optn='', log_level='error') -> FFProbeResult:

    assert ffprobe_format in ['json', 'flat'], "format must be json or flat, not %s" % ffprobe_format
    format_optn = '=' + format_optn if format_optn else format_optn
    command_array = ["ffprobe",
                     "-v", log_level,
                     "-print_format", ffprobe_format + format_optn,
                     '-show_programs',
                     "-show_format",
                     "-show_streams",
                     f"{file_path}"]
    try:
        encoding = 'cp850'
        result = subprocess.run(command_array, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True, encoding=encoding)
    except Exception as e:
        logging.critical("ffprobe failed to run on %s, with the following error: '%s'\n"
                        " check first that cmd is in your path",
                        file_path, result.stderr, exc_info=True)
        raise e

    return FFProbeResult(return_code=result.returncode,
                         output=result.stdout,
                         error=result.stderr,
                         format=ffprobe_format)