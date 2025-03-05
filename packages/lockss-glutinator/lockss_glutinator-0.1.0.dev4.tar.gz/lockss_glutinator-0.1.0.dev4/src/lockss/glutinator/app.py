#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Mimicking what datamodel-codegen does, not sure if it's because of --target-python-version=3.9
from __future__ import annotations

import json
import tarfile
from pathlib import Path
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field
from split_file_reader import SplitFileReader
import yaml

class GlutinatorConfigModel(BaseModel):
    kind: Literal['glutinator-configuration']
    id: str
    name: str
    source_aus: Optional[List[str]] = Field(None, alias='source-aus')

class GlutinatorApp(object):

    def __init__(self):
        super().__init__()
        self._config: Optional[GlutinatorConfigModel] = None

    def load_configuration(self, path: Path):
        loaded_obj = self._load_json_or_yaml(path)
        self._config = GlutinatorConfigModel(**loaded_obj)

    def unpack_sources(self):
        inbase = Path('sources')
        if not inbase.exists():
            raise FileNotFoundError(f'{inbase!r}')
        outbase = Path('sources-unpacked')
        for nickname in (self._config.source_aus or list()):
            outdir = Path(outbase, nickname)
            outdir.mkdir(parents=True, exist_ok=True)
            single = Path(inbase, f'{nickname}.tgz')
            if single.exists():
                with tarfile.open(single, 'r:gz') as tgz:
                    tgz.extractall(outdir)
            else:
                width = 0
                while width < 4:
                    if Path(inbase, f'{nickname}.tgz.{0:0{width}d}').exists():
                        break
                    width = width + 1
                if width == 4:
                    raise FileNotFoundError(', '.join(f'{nickname}.tgz.{0:0{pad}d}' for pad in range(0, 4)))
                file_list = list()
                i = 0
                while True:
                    f = Path(inbase, f'{nickname}.tgz.{i:0{width}d}')
                    if not f.exists():
                        break
                    file_list.append(f)
                    i = i + 1
                with SplitFileReader(file_list) as splitf, tarfile.open(fileobj=splitf, mode='r:gz') as tgz:
                    tgz.extractall(outdir)

    def _load_json_or_yaml(self, path: Path) -> Any:
        with path.open('r') as fin:
            if path.suffix == '.json':
                return json.load(fin)
            else:
                return yaml.safe_load(fin)
