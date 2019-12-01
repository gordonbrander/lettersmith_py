"""
Tools for indexing docs by tag (taxonomy).
"""
from datetime import datetime
from lettersmith.func import composable, pipe
from lettersmith import path as pathtools
from lettersmith import stub as Stub
from lettersmith import doc as Doc
from lettersmith import docs as Docs
from lettersmith.lens import lens_compose, key, get, put


_empty = tuple()


meta_related = lens_compose(Doc.meta, key("related", _empty))


def meta_taxonomy(tax):
    """
    Create a lens for taxonomy `tax`.
    """
    return lens_compose(Doc.meta, key(tax, _empty))


meta_tags = meta_taxonomy("tags")


@composable
def taxonomy_archives(
    docs,
    key,
    template="taxonomy.html",
    output_path_template="{taxonomy}/{term}/index.html"
):
    """
    Creates an archive page for each taxonomy term. One page per term.
    """
    tax_index = index_taxonomy(docs, key)
    for term, docs in tax_index.items():
        output_path = output_path_template.format(
            taxonomy=pathtools.to_slug(key),
            term=pathtools.to_slug(term)
        )
        meta = {"docs": docs}
        now = datetime.now()
        yield Doc.create(
            id_path=output_path,
            output_path=output_path,
            created=now,
            modified=now,
            title=term,
            template=template,
            meta=meta
        )


tag_archives = taxonomy_archives("tags")


def _get_indexes(index, keys):
    for key in keys:
        for item in index[key]:
            yield item


@composable
def index_taxonomy(docs, key):
    """
    Create a new index for a taxonomy.
    `key` is a whitelisted meta keys that should
    be treated as a taxonomy field.

    Returns a dict that looks like:

        {
            "term_a": [stub, ...],
            "term_b": [stub, ...]
        }
    """
    tax_index = {}
    for doc in docs:
        if key in doc.meta:
            for term in doc.meta[key]:
                if term not in tax_index:
                    tax_index[term] = []
                tax_index[term].append(Stub.from_doc(doc))
    return tax_index


index_tags = index_taxonomy("tags")


def related(tax):
    """
    Annotate doc meta with a list of related doc stubs.

    A doc is related if it shares any of the same tags in the
    same taxonomy.
    """
    taxonomy = meta_taxonomy(tax)
    build_index = index_taxonomy(tax)
    def add_related(docs):
        docs = tuple(docs)
        index = build_index(docs)
        for doc in docs:
            tags = get(taxonomy, doc)
            related = pipe(
                _get_indexes(index, tags),
                Docs.dedupe,
                Docs.remove_id_path(doc.id_path),
                tuple
            )
            yield put(meta_related, doc, related)
    return add_related


related_by_tag = related("tags")