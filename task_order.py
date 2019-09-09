import itertools as it

def gen_interface_order(
    names=("dwell-time_buttons", 
    "dwell-time_regions", 
    "enter-and-leave_regions"),
    amount=30):
    cycle = it.cycle(it.permutations(names))
    ret = []
    for i in range(amount):
        ret.append(next(cycle))
    return ret

if __name__ == "__main__":
    import glob
    permuts = gen_interface_order(amount=40)
    for subject, task_order in zip(glob.glob("./data_temp/*"), permuts):
        with open(subject + '/task_order', 'w') as f:
            for task in task_order:
                f.write(task + '\n')
