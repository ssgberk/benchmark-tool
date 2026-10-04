from toolset.github_actions.github_actions_diff import changed_tests

ALL = ["Go/hugo", "Ruby/jekyll", "Rust/zola"]


def test_only_touched_generators():
    assert changed_tests(["Ruby/jekyll/Gemfile", "README.md"], ALL) == ["Ruby/jekyll"]


def test_canonical_build_sh_runs_all():
    assert changed_tests(["Go/hugo/build.sh"], ALL) == ALL


def test_deleted_generator_is_skipped():
    assert changed_tests(["JavaScript/harp-ejs/build.sh"], ALL) == []


def test_ci_files_run_all():
    assert changed_tests([".github/workflows/ci.yml"], ALL) == ALL
