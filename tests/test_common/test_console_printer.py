import freezegun
import pytest

from hidori_common.cli import ConsolePrinter


@pytest.fixture(scope="module")
def printer() -> ConsolePrinter:
    return ConsolePrinter(user="root", target="machine")


def test_print_summary_stub(
    capsys: pytest.CaptureFixture[str], printer: ConsolePrinter
):
    printer.print_summary()
    assert capsys.readouterr().out == "\n"


@freezegun.freeze_time("2022-10-13 20:30:15")
def test_print_single_message(
    capsys: pytest.CaptureFixture[str], printer: ConsolePrinter
):
    data = {"task": "Hello World", "type": "success", "message": "It worked"}

    printer.print_one(data)
    output = capsys.readouterr().out.splitlines()
    assert len(output) == 2
    assert output[0] == "\x1b[1m[root@machine: Hello World]\x1b[0m"
    assert output[1] == "[Oct 13 20:30:15] \x1b[1m\x1b[32mOK:\x1b[39m\x1b[0m It worked"
