import sys, os, subprocess, time
import re
import json
from os import listdir
from os.path import isfile, join
from typing import List, Union

IMAGE_NAME = "sochi"
BASE_DIR = os.path.join(os.path.dirname(__file__))
BENCHMARK_DIR = os.path.join(BASE_DIR, "benchmarks")

def run_cmd(cmd_str):
    print("[*] Executing: %s" % cmd_str)
    cmd_args = cmd_str.split()
    try:
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        return str(output.decode('UTF-8'))
    except Exception as e:
        print(e)
        exit(1)

def run_cmd_in_docker(container, cmd_str):
    cmd_prefix = "docker exec -d %s /bin/bash -c" % container
    cmd_args = cmd_prefix.split()
    cmd_args += [cmd_str]
    print("[*] Executing (in container): %s" % cmd_args)
    try:
        PIPE = subprocess.PIPE
        p = subprocess.Popen(cmd_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        return str(output.decode('UTF-8'))
    except Exception as e:
        print(e)
        exit(1)

def check_cpu_count(MAX_INSTANCE_NUM):
    n_str = run_cmd("nproc")
    try:
        if int(n_str) < MAX_INSTANCE_NUM:
            print("Not enough CPU cores, please decrease MAX_INSTANCE_NUM")
            exit(1)
    except Exception as e:
        print(e)
        print("Failed to count the number of CPU cores, abort")
        exit(1)

def decide_outdir():
    prefix = "confuzzius"
    i = 0
    while True:
        i += 1
        filedir = "output-%s-%d" % (prefix, i)
        outdir = os.path.join(BASE_DIR, filedir)
        if not os.path.exists(outdir):
            return outdir

def get_targets(path):
    # Initialize an empty list to store file paths
    file_paths = []

    # Iterate through all files and directories in the given path
    for root, _, files in os.walk(path):
        for filename in files:
            # Add the file path to the list
            if filename.endswith(".sol"):
                file_paths.append(os.path.join(root, filename))

    # Return the list of file paths
    return file_paths

def fetch_works(targets, MAX_INSTANCE_NUM):
    works = []
    for _ in range(MAX_INSTANCE_NUM):
        if len(targets) <= 0:
            break
        works.append(targets.pop(0))
    return works

def spawn_containers(targets):
    for i in range(len(targets)):
        targ = os.path.basename(targets[i])
        cmd = "docker run --rm -m=6g --cpuset-cpus=%d -it -d --name %s %s" % \
                (i, targ, IMAGE_NAME)
        run_cmd(cmd)

def run_fuzzing(targets, timelimit):
    for targ in targets:
        src = "/home/test/" + targ
        output = src + ".json"
        args = "%d %s %s" % (timelimit, src, output)
        script = "/home/test/scripts/run_confuzzius.sh"
        cmd = "%s %s" % (script, args)
        run_cmd_in_docker(os.path.basename(targ), cmd)
    time.sleep(timelimit + 2)

def store_outputs(targets, outdir):
    for targ in targets:
        input_file = targ
        file_dir = os.path.dirname(targ)
        file_outdir = os.path.join(outdir, file_dir)
        if not os.path.exists(file_outdir):
            os.makedirs(file_outdir)

        targ = os.path.basename(targ)
        output_dir = os.path.join(file_outdir, targ)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        cmd = "docker cp %s:/home/test/output/ %s" % (targ, output_dir)

        json_file = os.path.join(output_dir, "output.json")
        f = open(json_file, "w")
        f.write(f'test_file = """{input_file}"""\n\n')
        f.close()

        run_cmd(cmd)

def remove_prefix(string: str, prefix) -> str:
    if string.startswith(prefix):
        new_string = string[len(prefix):]

    return new_string

def interpret_outputs(targets, outdir):
    for target in targets:
        target_outdir = os.path.join(outdir, target)
        output_dir = os.path.join(target_outdir, "output")
        output_file = os.path.join(output_dir, os.path.basename(target) + ".json")
        output = None

        with open(output_file, "r", encoding="utf-8") as file:
            try:
                output = json.load(file)
            except ValueError:
                return;

        if output is None:
            return;

        issues = []
        coverage = []
        all_results = list(output.values())
        results = all_results[0]
        error_list = results.get("errors")
        generations = results.get("generations")
        errors = list(error_list.values())

        for error_desc in errors:
            error = error_desc[0]
            issue = error.get("type")
            issues.append(issue)

        for generation in generations:
            code_coverage = generation.get("code_coverage")
            branch_coverage = generation.get("branch_coverage")
            coverage.append((code_coverage, branch_coverage))

        json_file = os.path.join(target_outdir, "output.json")
        f = open(json_file, "a")
        f.write(f'issues = """{issues}"""\n\n')
        print(f'issues = """{issues}"""\n\n')
        f.write(f'coverage = """{coverage}"""\n\n')
        f.close


def cleanup_containers(targets):
    for targ in targets:
        targ = os.path.basename(targ)
        cmd = "docker kill %s" % targ
        run_cmd(cmd)

def main():
    if len(sys.argv) != 4:
        print("Usage: %s <benchmark> <timelimit <MAX_INSTANCE_NUM>" % \
              sys.argv[0])
        exit(1)

    benchmark = sys.argv[1]
    timelimit = int(sys.argv[2])
    MAX_INSTANCE_NUM = int(sys.argv[3])

    check_cpu_count(MAX_INSTANCE_NUM)
    outdir = decide_outdir()
    print(f"outdir: {outdir}")
    os.makedirs(outdir)
    targets = get_targets(benchmark)
    while len(targets) > 0:
        work_targets = fetch_works(targets, MAX_INSTANCE_NUM)
        spawn_containers(work_targets)
        run_fuzzing(work_targets, timelimit)
        store_outputs(work_targets, outdir)
        interpret_outputs(work_targets, outdir)
        cleanup_containers(work_targets)

if __name__ == "__main__":
    main()
