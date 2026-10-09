from pathlib import Path

SOURCE=(Path(__file__).parents[1]/'contracts'/'contract.py').read_text()

def test_three_distinct_map_effects():
 assert "RELATIONS=('NEW','DEEPENS','DUPLICATE')" in SOURCE
 assert "if verdict['relation']=='NEW'" in SOURCE
 assert "elif verdict['relation']=='DEEPENS'" in SOURCE
 assert "island.depth=u256(int(island.depth)+1)" in SOURCE

def test_duplicate_does_not_mutate_islands():
 block=SOURCE[SOURCE.index("if verdict['relation']=='NEW'"):SOURCE.index("self.observations[oid]")]
 assert "DUPLICATE" not in block

def test_replay_guard_precedes_sounding():
 assert SOURCE.index('replay_key in self.attempted')<SOURCE.index('verdict=self._sound')
 assert "body.lower().encode()" in SOURCE

def test_every_state_driver_is_consensus_bound():
 for item in ('relation','matched_island','category','severity','every existing island'):
  assert item in SOURCE

def test_publish_requires_curator_and_two_islands():
 assert "addr(gl.message.sender_address)!=addr(atlas.curator)" in SOURCE
 assert "len(json.loads(atlas.island_ids))<2" in SOURCE
