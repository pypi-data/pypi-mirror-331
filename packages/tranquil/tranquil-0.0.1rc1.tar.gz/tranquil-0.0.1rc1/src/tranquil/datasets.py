from datasets import load_dataset, DatasetDict

__all__ = [
    "TaskDict",
]


class TaskDict:
    def __init__(self, datasets: DatasetDict, tasks: list[str]):
        self.datasets = datasets
        self.tasks = tasks

    def __len__(self):
        return len(self.tasks)

    def __getitem__(self, index: int) -> DatasetDict:
        task_id = self.tasks[index]
        return DatasetDict(
            {
                split: self.datasets[split].filter(lambda x: x["task_id"] == task_id)
                for split in self.datasets.keys()
            }
        )


def load_tasks(path: str, index: int = 0) -> TaskDict:
    tasks = [
        next(zip(*sorted(order.items(), key=lambda x: x[1])))
        for order in load_dataset(path, "tasks", split="train")
    ][index]
    datasets = load_dataset(path)
    return TaskDict(datasets, tasks)
