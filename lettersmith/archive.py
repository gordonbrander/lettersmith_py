"""
Generate an archive page.
"""
from lettersmith import doc as Doc
from lettersmith import stub as Stub
from lettersmith.func import composable


@composable
def archive(
    docs,
    output_path,
    title="Archive",
    template="archive.html"
):
    """
    Generate an archive doc for a list of docs.
    """
    archive = tuple(Stub.stubs(docs))
    return Doc.create(
        id_path=output_path,
        output_path=output_path,
        title=title,
        content="",
        template=template,
        meta={"archive": archive}
    )