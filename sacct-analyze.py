#!/usr/bin/env python3

# Copyright (c) 2025 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import json
import subprocess
import tempfile
import typing

def get_sacct_data():
    with tempfile.TemporaryFile("wb+") as outfile:
        subprocess.run(["sacct", "--json"], stdout=outfile, check=True)
        outfile.seek(0)
        data = json.load(outfile)
    return data


class SlurmJob(typing.NamedTuple):
    job_name: str
    cpu: int
    memory: int
    time: int
    elapsed_time: int
    cpu_time: float
    max_rss: float
    @classmethod
    def from_job_dict(cls, job_dict):
        allocated_cpu = 0
        allocated_memory = 0
        max_rss = 0
        for d in job_dict["tres"]["allocated"]:
            tp = d["type"]
            if tp == "cpu":
                allocated_cpu = d["count"]
            elif tp == "mem":
                allocated_memory = d["count"]
        for d in job_dict["steps"]:
            if d["step"]["id"]["step_id"] == "0":
                for used in d["tres"]["requested"]["max"]:
                    type = used["type"]
                    if type == "mem":
                        max_rss = used["count"] / (1024 * 1024)

        return cls(
            job_name=job_dict["name"],
            elapsed_time=job_dict["time"]["elapsed"],
            cpu_time = (job_dict["time"]["total"]["seconds"] +
                        job_dict["time"]["total"]["microseconds"] / 10 ** 6),
            memory=allocated_memory,
            cpu=allocated_cpu,
            time = job_dict["time"]["limit"]["number"] * 60,
            max_rss=max_rss,
        )
