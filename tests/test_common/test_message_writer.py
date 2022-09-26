from pytest import CaptureFixture

from hidori_common.cli import CLIMessageWriter


def test_print_summary_stub(capsys: CaptureFixture[str]):
    message_writer = CLIMessageWriter(user="root", target="machine")
    message_writer.print_summary()
    assert capsys.readouterr().out == "\n"
