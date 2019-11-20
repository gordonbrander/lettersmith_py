"""
Tools for indexing docs by tag (taxonomy).
"""
from datetime import datetime
from lettersmith.func import composable
from lettersmith import path as pathtools
from lettersmith.doc import doc


@composable
def taxonomy_archives(
    docs,
    key,
    templates=tuple(),
    output_path_template="{taxonomy}/{term}/all/index.html"
):
    """
    Creates an archive page for each taxonomy term. One page per term.
    """
    tax_index = index_by_taxonomy(docs, key)
    for term, docs in tax_index.items():
        output_path = output_path_template.format(
            taxonomy=pathtools.to_slug(key),
            term=pathtools.to_slug(term)
        )
        tax_templates = (
            "taxonomy/{}/all.html".format(key),
            "taxonomy/{}/list.html".format(key),
            "taxonomy/all.html",
            "taxonomy/list.html",
            "list.html"
        )
        meta = {"docs": docs}
        now = datetime.now()
        yield doc(
            id_path=output_path,
            output_path=output_path,
            created=now,
            modified=now,
            title=term,
            section=key,
            templates=(*templates, *tax_templates),
            meta=meta
        )


tag_archives = taxonomy_archives("tags")


@composable
def index_taxonomy(docs, key):
    """
    Create a new index for a taxonomy.
    `key` is a whitelisted meta keys that should
    be treated as a taxonomy field.

    Returns a dict that looks like:

        {
            "term_a": [doc, ...],
            "term_b": [doc, ...]
        }
    """
    tax_index = {}
    for doc in docs:
        if key in doc.meta:
            for term in doc.meta[key]:
                if term not in tax_index:
                    tax_index[term] = []
                tax_index[term].append(doc)
    return tax_index


index_tags = index_taxonomy("tags")

