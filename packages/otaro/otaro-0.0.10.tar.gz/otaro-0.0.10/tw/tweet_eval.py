import os
from pathlib import Path

from otaro import Task


def main() -> None:
    file_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    task = Task.from_config(file_dir / "tweet_generator.yml")
    with open(file_dir / "blogpost.txt") as file:
        blog_content = file.read()

    score, _ = task.evaluate(
        [
            {
                "blog_content": blog_content,
                "tweet_count": 2,
                "tone_preference": "engaging",
            }
        ]
        * 5,
        verbose=True,
    )
    print(score)


if __name__ == "__main__":
    main()
