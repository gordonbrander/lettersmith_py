"""
Tools for indexing docs by tag (taxonomy).
"""
DEFAULT_TAXONOMIES = ("tag",)
_EMPTY_TUPLE = tuple()


def items_with_keys(d, keys):
    return ((key, value) for key, value in d.items() if key in keys)


def index_by_taxonomy(stubs, taxonomies=None):
    """
    Create a new index by taxonomy.
    `taxonomies` is an indexable whitelist of meta keys that should
    be treated as taxonomies.

    Returns a dict that looks like:

        {
            "taxonomy_name": {
                "term_a": [doc, ...],
                "term_b": [doc, ...]
            }
        }
    """
    taxonomies = taxonomies or DEFAULT_TAXONOMIES
    tax_index = {}
    for stub in stubs:
        for tax, terms in items_with_keys(stub["meta"], taxonomies):
            if not tax_index.get(tax):
                tax_index[tax] = {}
            for term in terms:
                if not tax_index[tax].get(term):
                    tax_index[tax][term] = []
                tax_index[tax][term].append(stub)
    return tax_index