from utils.data_engine import AEBDataEngine

sample = [
    {
        'success': True,
        'filename': 'sample1.txt',
        'text': '2020 transformer attention language model pretraining representation learning neural network',
    },
    {
        'success': True,
        'filename': 'sample2.txt',
        'text': '2021 transformer language model instruction tuning alignment evaluation neural network',
    },
    {
        'success': True,
        'filename': 'sample3.txt',
        'text': '2022 retrieval augmented generation language model knowledge graph evaluation',
    },
]

config = {
    'ecology': {
        'top_predator_percentile': 0.01,
        'dominant_percentile': 0.10,
        'niche_levels': 5,
        'louvain_resolution': 1.0,
    }
}

engine = AEBDataEngine()
engine.ingest(sample)
engine.compute_all(config)

assert engine.is_computed
assert len(engine.papers_df) == 3
assert len(engine.keywords_df) > 0
assert 'keyword' in engine.keywords_df.columns
assert isinstance(engine.to_json(), dict)

print('AEB smoke test passed.')
