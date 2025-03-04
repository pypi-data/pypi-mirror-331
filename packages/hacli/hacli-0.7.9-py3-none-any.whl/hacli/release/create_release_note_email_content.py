import os

import typer
from typing_extensions import Annotated

app = typer.Typer()


@app.command(name="create_release_note_email_content",
             help="生成 release note 邮件内容",
             short_help="生成邮件内容")
def create_release_note_email_content(
        release: Annotated[str, typer.Argument(help="前一个版本号，例如：1.0.0")],
) -> str:
    return os.environ["RELEASE_NOTE_EMAIL_TEMPLATE"].format(release=release)
