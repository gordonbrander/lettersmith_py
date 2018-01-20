def map_patch(docs, patch):
    """
    Patch a doc object, merging patch deeply with doc.
    For any property collision, the property value in `patch` wins.
    """
    return (merge_deep(doc, patch) for doc in docs)