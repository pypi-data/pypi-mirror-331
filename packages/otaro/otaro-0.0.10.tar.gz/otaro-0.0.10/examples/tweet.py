import os
from pathlib import Path

from otaro import Task


def main():
    file_dir = Path(os.path.dirname(os.path.realpath(__file__)))
    task = Task.from_config(file_dir / "tweet_generator.yml")
    response = task.run(
        blog_content="Since launching, Zapier has caught the wave all while building an incredible surfboard. This has made them the de facto layer of no-code business logic, where non-technical users orchestrate the flow of data between tools that otherwise wouldn’t talk to each other.",
        tweet_count=3,
        tone_preference="engaging",
    )
    print(response.tweets)


if __name__ == "__main__":
    main()
