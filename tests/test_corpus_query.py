from docintelligence.core.models import CorpusQueryRequest
from docintelligence.corpus.service import corpus_stats, query_corpus


def test_corpus_stats_and_query() -> None:
    stats = corpus_stats()
    assert stats["document_count"] >= 1000
    assert stats["atom_count"] > 0

    response = query_corpus(CorpusQueryRequest(query="humanitarian data", top_k=3))

    assert response.total_docs >= 1000
    assert response.returned_hits >= 1
    assert response.hits[0].support_atom_ids
