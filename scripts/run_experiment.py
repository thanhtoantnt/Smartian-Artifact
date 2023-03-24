import sys, os, subprocess, time
from common import BASE_DIR, BENCHMARK_DIR
from os import listdir
from os.path import isfile, join

IMAGE_NAME = "sochi"
SUPPORTED_TOOLS = ["smartian", "sFuzz", "ilf", "mythril", "manticore"]

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

def decide_outdir(benchmark, tool):
    if benchmark.endswith("/"):
        prefix = benchmark + tool
    else:
        prefix = benchmark + "/" + tool
    i = 0
    while True:
        i += 1
        outdir = os.path.join(BASE_DIR, "output", "%s-%d" % (prefix, i))
        if not os.path.exists(outdir):
            return outdir

def decide_bench_dirname(benchmark):
    if benchmark.startswith("B"):
        return benchmark.split("-")[0]
    else:
        print("Unexpected benchmark: %s" % benchmark)
        exit(1)

def get_targets(benchmark):
    targets = []
    for filename in os.listdir(benchmark):
        if filename.endswith(".sol"):
            target = [os.path.join(benchmark, filename), filename]
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
        targ = os.path.basename(targets[i][0])
        cmd = "docker run --rm -m=6g --cpuset-cpus=%d -it -d --name %s %s" % \
                (i, targ, IMAGE_NAME)
        run_cmd(cmd)

def run_fuzzing(benchmark, targets, tool, timelimit, opt):
    # bench_dirname = decide_bench_dirname(benchmark)
    for targ in targets:
        print(targ)
        src = "/home/test/" + targ[0]
        args = "%d %s" % (timelimit, src)
        script = "/home/test/scripts/run_%s.sh" % tool
        cmd = "%s %s" % (script, args)
        print(cmd)
        run_cmd_in_docker(os.path.basename(targ[0]), cmd)
    time.sleep(timelimit + 2)

def store_outputs(targets, outdir):
    for targ in targets:
        input_file = targ[1]
        targ = os.path.basename(targ[0])
        cmd = "docker cp %s:/home/test/output/ %s/%s" % (targ, outdir, targ)

        print(f"store_output cmd: {cmd}")
        json_file = os.path.join(outdir, targ, "output.json")
        with open(json_file, "w", encoding="utf-8") as file:
            file.write(f'test_file = """{input_file}"""\n\n')

        run_cmd(cmd)

def cleanup_containers(targets):
    for targ in targets:
        targ = os.path.basename(targ[0])
        cmd = "docker kill %s" % targ
        run_cmd(cmd)

def main():
    if len(sys.argv) != 5:
        print("Usage: %s <benchmark> <tool> <timelimit <MAX_INSTANCE_NUM>" % \
              sys.argv[0])
        exit(1)

    benchmark = sys.argv[1]
    tool = sys.argv[2]
    timelimit = int(sys.argv[3])
    MAX_INSTANCE_NUM = int(sys.argv[4])
    opt = ""

    check_cpu_count(MAX_INSTANCE_NUM)
    if tool not in SUPPORTED_TOOLS:
        print("Unsupported tool: %s" % tool)
        exit(1)

    outdir = decide_outdir(os.path.basename(benchmark), tool)
    os.makedirs(outdir)
    print(f"outdir: {outdir}")
    targets = get_targets(benchmark)
    while len(targets) > 0:
        work_targets = fetch_works(targets, MAX_INSTANCE_NUM)
        spawn_containers(work_targets)
        run_fuzzing(benchmark, work_targets, tool, timelimit, opt)
        store_outputs(work_targets, outdir)
        cleanup_containers(work_targets)

if __name__ == "__main__":
    main()
