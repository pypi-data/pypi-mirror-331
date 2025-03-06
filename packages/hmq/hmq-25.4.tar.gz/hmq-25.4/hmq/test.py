import hmq
@hmq.task
def task(up_to) -> int:
    # imports within the function
    import numpy as np

    return (np.arange(up_to) * 2).sum()


task(10)
tag = task.submit(packages=["numpy"])
tag.pull(blocking=True)
print(list(tag.results))  # [90]

