import pytest


from jobs import __main__, _pyperformance, _utils


from .helpers import DEFAULT_ARGS, IDEAS_GIT_URL


def _setup_repo_root(tmp_path):
    repo_root = tmp_path / "ideas"

    github_target = _utils.GitHubTarget.from_url(IDEAS_GIT_URL)
    github_target.ensure_local(str(repo_root))

    # Monkey-patch
    _pyperformance.FasterCPythonResults._DEFAULT_ROOT = str(repo_root)


def test_compare(tmp_path, capsys):
    # This is just a simple smoke test

    _setup_repo_root(tmp_path)

    __main__._parse_and_main(
        DEFAULT_ARGS + [
            "compare",
            "cpython-3.12.0a0-c20186c397-fc_linux-b2cf916db80e-pyperformance",
            "cpython-3.10.4-9d38120e33-fc_linux-b2cf916db80e-pyperformance",
        ],
        __file__
    )

    expected = """
| Geometric mean          | (ref)                                                           | 1.3068x slower                                                |
+-------------------------+-----------------------------------------------------------------+---------------------------------------------------------------+

Benchmark hidden because not significant (1): pickle
Ignored benchmarks (6) of cpython-3.10.4-9d38120e33-fc_linux-b2cf916db80e-pyperformance.json: genshi_text, genshi_xml, gevent_hub, pylint, sqlalchemy_declarative, sqlalchemy_imperative
    """

    captured = capsys.readouterr()

    assert captured.out.strip().endswith(expected.strip())


def test_show(tmp_path):
    # This is just a simple smoke test

    _setup_repo_root(tmp_path)

    with pytest.raises(SystemExit) as exc:
        __main__._parse_and_main(
            DEFAULT_ARGS + [
                "show",
            ],
            __file__
        )

    assert exc.value.code == 1
