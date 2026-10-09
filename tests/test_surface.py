from pathlib import Path

HTML=(Path(__file__).parents[1]/'docs'/'index.html').read_text()

def test_map_workflow_is_complete():
 for item in ('CHART ATLAS','SOUND FIELD NOTE','PUBLISH MAP','FINALIZED','chart_atlas','sound_observation','publish_map','get_atlas'):
  assert item in HTML

def test_spatial_identity():
 for item in ('ocean-canvas','island-node','field-sheet','depth-contour'):
  assert item in HTML
 assert 'quota-ring' not in HTML and 'flight-strip' not in HTML and '<pre' not in HTML
