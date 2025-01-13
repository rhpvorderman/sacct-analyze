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

import argparse
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name",
                        help="Should have these contents in the name",
                        default="")
    args = parser.parse_args()
    search_name = args.name
    sacct_data = get_sacct_data()
    print(
        "Name\t"
        "Requested CPU\tAvailable CPU time (hours)\tUsed CPU time (hours)\t"
        "CPU Efficiency (%)\t"
        "Requested Memory (GiB)\tUsed Memory (GiB)\tMemory efficiency (%)\t"
        "Requested Time (hours)\tUsed Time (hours)\tTime Efficiency (%)")
    for job_dict in sacct_data["jobs"]:
        job = SlurmJob.from_job_dict(job_dict)
        if search_name not in job.job_name:
            continue
        elapsed_time = job.elapsed_time / 3600
        requested_time = job.time / 3600
        available_cpu_time = elapsed_time * job.cpu
        cpu_time = job.cpu_time / 3600
        print(f"{job.job_name}\t"
              f"{job.cpu}\t{available_cpu_time:.2f}\t{cpu_time:.2f}\t"
              f"{available_cpu_time/cpu_time:.2%}\t"
              f"{job.memory / 1024:.2f}\t{job.max_rss/1024:.2f}\t"
              f"{job.max_rss/job.memory:.2%}\t"
              f"{requested_time}\t{elapsed_time}\t"
              f"{requested_time / elapsed_time:.2%}"
          )

