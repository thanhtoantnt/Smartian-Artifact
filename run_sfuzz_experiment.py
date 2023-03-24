import sys, os, subprocess, time
import re
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

def decide_outdir(benchmark):
    if benchmark.endswith("/"):
        prefix = benchmark + "sFuzz"
    else:
        prefix = benchmark + "/" + "sFuzz"
    i = 0
    while True:
        i += 1
        outdir = os.path.join(BASE_DIR, "output", "%s-%d" % (prefix, i))
        if not os.path.exists(outdir):
            return outdir

def get_targets(benchmark):
    targets = []
    for filename in os.listdir(benchmark):
        if filename.endswith(".sol"):
            target = os.path.join(benchmark, filename)
            targets.append(target)
    return targets

def fetch_works(targets, MAX_INSTANCE_NUM):
    works = []
    for i in range(MAX_INSTANCE_NUM):
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

def run_fuzzing(benchmark, targets, timelimit, opt):
    for targ in targets:
        print(targ)
        src = "/home/test/" + targ
        args = "%d %s" % (timelimit, src)
        script = "/home/test/scripts/run_sFuzz.sh"
        cmd = "%s %s" % (script, args)
        print(cmd)
        run_cmd_in_docker(os.path.basename(targ), cmd)
    time.sleep(timelimit + 2)

def store_outputs(targets, outdir):
    for targ in targets:
        input_file = targ
        targ = os.path.basename(targ)
        cmd = "docker cp %s:/home/test/output/ %s/%s" % (targ, outdir, targ)

        print(f"store_output cmd: {cmd}")
        file_outdir = os.path.join(outdir, targ)
        os.makedirs(file_outdir)
        json_file = os.path.join(file_outdir, "output.json")
        f = open(json_file, "w")
        f.write(f'test_file = """{input_file}"""\n\n')
        f.close()

        run_cmd(cmd)

def parse_sfuzz_coverage(log_file: str) :
    lines = None
    with open(log_file, "r", encoding="utf-8") as file:
        try:
            lines = [line.rstrip() for line in file]
        except ValueError:
            return []

    count = 1
    pair = [(0, 0)]
    for line in lines:
        match_str = re.search(r"coverage : [0-9]+", line)
        if match_str:
            coverage = match_str.group()
            coverage = coverage.removeprefix("coverage : ")
            pair.append((count, int(coverage)))
            count += 1
            result = coverage

    return pair

def interpret_outputs(targets, outdir):
    for targ in targets:
        targ = os.path.basename(targ)
        file_outdir = os.path.join(outdir, targ)
        output_dir = os.path.join(file_outdir, "output")
        log_file = os.path.join(output_dir, "log.txt")
        stdout_file = os.path.join(output_dir, "stdout.txt")
        pairs = parse_sfuzz_coverage(stdout_file)
        print(pairs)

        lines = None
        with open(log_file, "r", encoding="utf-8") as file:
            lines = [line.rstrip() for line in file]

        issues = []
        for line in lines:
            if "MishandledException" in line:
                issues.append("UNHANDLED_EXCEPTION");

            if "Reentrancy" in line:
                issues.append("REENTRANCY");

            if "IntegerBug" in line:
                issues.append("INTEGER_BUG");

            if "DeletegateCall" in line:
                issues.append("UNSAFE_DELEGATECALL");

            if "LockEther" in line:
                issues.append("LOCKING_ETHER");

            if "BlockstateDependency" in line:
                issues.append("BLOCK_DEPENDENCY");

        print(f"issues: {issues}")
        json_file = os.path.join(file_outdir, "output.json")
        f = open(json_file, "a")
        f.write(f'issues = """{issues}"""\n\n')
        f.write(f'coverage = """{issues}"""\n\n')
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
    opt = ""

    check_cpu_count(MAX_INSTANCE_NUM)
    outdir = decide_outdir(os.path.basename(benchmark))
    os.makedirs(outdir)
    print(f"outdir: {outdir}")
    targets = get_targets(benchmark)
    while len(targets) > 0:
        work_targets = fetch_works(targets, MAX_INSTANCE_NUM)
        spawn_containers(work_targets)
        run_fuzzing(benchmark, work_targets, timelimit, opt)
        store_outputs(work_targets, outdir)
        interpret_outputs(work_targets, outdir)
        cleanup_containers(work_targets)

if __name__ == "__main__":
    main()
