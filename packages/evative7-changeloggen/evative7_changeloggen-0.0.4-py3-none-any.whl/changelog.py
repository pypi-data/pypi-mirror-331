import argparse
import os
import re
import subprocess

type_infos = [
    {"display": "Features", "include": ["feat"]},
    {"display": "Bug Fixes", "include": ["fix"]},
    {"display": "Improvements", "include": ["perf"]},
    {"display": "Docs", "include": ["docs"]},
    {"display": "Others", "include": ["chore", "refactor"], "display_origin": True},
]


def _call(command: str):
    """Run a command and return the output, handling errors gracefully."""
    command: list = command.split(" ")
    return subprocess.check_output(
        command, text=True, stderr=subprocess.DEVNULL
    ).strip()


def parse_conventional_commit(commit_message):
    """
    Parses submission information that complies with the Conventional Commitments specification.

    :param commit_message: Submit information string
    :return: Returns a dictionary containing the type, scope, theme, and disruptive change information (if any) of the submission
    """
    # Regular expressions used to resolve commit information that conforms to Conventional Commitments
    pattern = r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking_change>!?):\s*(?P<subject>.+?)\s*$"

    match = re.match(pattern, commit_message.strip())

    if not match:
        return None

    # Extract information from matching results
    commit_info = match.groupdict()

    # Add field identification if there is a disruptive change
    commit_info["breaking_change"] = commit_info["breaking_change"] == "!"

    commit_info["origin"] = commit_message

    return commit_info


def get_current_commit_hash():
    """Get the hash of the current commit."""
    return _call("git rev-parse HEAD")


def get_tags():
    """Get all tags that match semantic versioning and sort them in ascending order."""
    tags = _call("git tag").splitlines()

    # Regular expression for semantic versioning (SemVer)
    semver_regex = re.compile(
        r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
        r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
    )

    semantic_tags = [tag for tag in tags if semver_regex.match(tag)]
    return sorted(
        semantic_tags,
        key=lambda x: [
            int(n) if n.isdigit() else n for n in re.split(r"[.-]", x.lstrip("v"))
        ],
    )


def get_commit_messages(from_, to, contains_from=False):
    """Get Git commit logs between from_commit and to_commit."""
    log_range = f"{from_} {to}" if contains_from else f"{from_}..{to}"
    return _call(f"git log {log_range} --no-merges --pretty=format:%s").splitlines()


def generate_changelog(from_, to, all_msgs):
    """Generate content for CHANGELOG.md with a range of commits."""
    # changelog = f"## Changelog from {from_commit} to {to_commit}\n\n"
    changelog = ""
    for type_info in type_infos:
        msgs = [msg for msg in all_msgs if msg["type"] in type_info["include"]]
        if msgs:
            changelog += f"### {type_info['display']}\n\n"
            for msg in msgs:
                changelog += f"* "
                if type_info.get("display_origin"):
                    changelog += msg["origin"]
                else:
                    if msg["scope"]:
                        changelog += f"({msg['scope']}) "
                    changelog += msg["subject"]
                changelog += "\n"
            changelog += "\n"
    return changelog


def validate_git():
    """Check if Git installed."""
    try:
        _call("git --version")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Git is not installed.")
        exit(1)


def validate_git_repo():
    """Check if the current directory is a Git repository with commits."""
    try:
        _call("git log")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(
            "Either this is not a repository, or this repository does not contain commits."
        )
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate changelog from Git commits.")
    parser.add_argument("dir", help="Directory to run Git commands in")
    args = parser.parse_args()

    if args.dir:
        if not os.path.isdir(args.dir):
            print(f"Directory {args.dir} does not exist.")
            exit(1)
        os.chdir(args.dir)

    validate_git()
    validate_git_repo()
    current_commit = get_current_commit_hash()
    tags = get_tags()

    try:
        exact_match = _call(f"git describe --tags --exact-match {current_commit}")
        to = exact_match if exact_match in tags else current_commit

        to_a_tag = True
    except subprocess.CalledProcessError:
        to = current_commit

        to_a_tag = False

    from_tag_index = -2 if to_a_tag else -1

    if len(tags) > -1 - from_tag_index:
        from_ = tags[from_tag_index]
        from_a_tag = True
    else:
        from_ = _call("git rev-list --max-parents=0 HEAD")
        from_a_tag = False

    print(f"From {from_}, to {to}")
    all_msgs = [
        parsed
        for origin_msg in get_commit_messages(from_, to, not from_a_tag)
        if (parsed := parse_conventional_commit(origin_msg))
    ]

    changelog = generate_changelog(from_, to, all_msgs)
    print(changelog, end="\n\n\n")
    with open("CHANGELOG.md", "w") as file:
        file.write(changelog)

    print("Changelog generated successfully as CHANGELOG.md")


if __name__ == "__main__":
    main()
