# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""RiskArchipelago: a semantic map that distinguishes new, deepening, and duplicate risk observations."""
from genlayer import *
from dataclasses import dataclass
import hashlib,json,re

RELATIONS=('NEW','DEEPENS','DUPLICATE')
def clean(value,limit=1200): return " ".join(str(value).strip().split())[:limit]
def ident(value):
 key=clean(value,64).upper()
 if not re.fullmatch(r'[A-Z0-9][A-Z0-9_-]{2,63}',key): raise gl.vm.UserError('[EXPECTED] valid identifier required')
 return key
def addr(value):
 raw=value.as_hex if hasattr(value,'as_hex') else str(value).strip()
 if not re.fullmatch(r'0x[0-9a-fA-F]{40}',raw): raise gl.vm.UserError('[EXPECTED] valid wallet required')
 return raw.lower()
def obj(value):
 if isinstance(value,dict): return value
 text=str(value); start=text.find('{'); end=text.rfind('}')
 if start<0 or end<=start: raise gl.vm.UserError('[LLM] JSON object required')
 try: result=json.loads(text[start:end+1])
 except: raise gl.vm.UserError('[LLM] invalid JSON')
 if not isinstance(result,dict): raise gl.vm.UserError('[LLM] JSON object required')
 return result

@allow_storage
@dataclass
class Atlas:
 curator: Address
 title: str
 scope: str
 categories: str
 state: str
 island_ids: str
 observation_ids: str

@allow_storage
@dataclass
class Island:
 atlas_id: str
 anchor_observation_id: str
 title: str
 category: str
 severity: u256
 depth: u256

@allow_storage
@dataclass
class Observation:
 reporter: Address
 atlas_id: str
 title: str
 note: str
 note_digest: str
 relation: str
 matched_island: str
 category: str
 severity: u256

class RiskArchipelago(gl.Contract):
 atlases: TreeMap[str,Atlas]
 islands: TreeMap[str,Island]
 observations: TreeMap[str,Observation]
 attempted: TreeMap[str,bool]

 def _atlas(self,atlas_id):
  key=ident(atlas_id)
  if key not in self.atlases: raise gl.vm.UserError('[EXPECTED] atlas not found')
  return key,self.atlases[key]
 def _sound(self,scope,categories,existing,title,note):
  def run():
   prompt='Risk Archipelago sounding. Compare FIELD_NOTE with the existing risk islands inside SCOPE. relation must be NEW when it introduces a materially distinct risk, DEEPENS when it adds a distinct mechanism or consequence to one existing island, or DUPLICATE when it merely restates one. matched_island must be empty for NEW and the exact island id otherwise. Choose one CATEGORY and integer severity 1..5. JSON only {"relation":"NEW","matched_island":"","category":"CATEGORY","severity":1}. SCOPE:'+scope+' CATEGORIES:'+json.dumps(categories)+' EXISTING:'+json.dumps(existing,sort_keys=True)+' FIELD_NOTE:'+title+' / '+note
   result=obj(gl.nondet.exec_prompt(prompt,response_format='json')); relation=clean(result.get('relation',''),16).upper(); matched=clean(result.get('matched_island',''),64).upper(); category=ident(result.get('category',''))
   try: severity=int(result.get('severity',0))
   except: severity=0
   island_ids=[item['id'] for item in existing]
   if relation not in RELATIONS or category not in categories or severity<1 or severity>5: raise gl.vm.UserError('[LLM] bounded sounding required')
   if relation=='NEW' and matched: raise gl.vm.UserError('[LLM] new observation cannot match an island')
   if relation!='NEW' and matched not in island_ids: raise gl.vm.UserError('[LLM] existing island match required')
   return {'relation':relation,'matched_island':matched,'category':category,'severity':severity}
  return gl.eq_principle.prompt_comparative(run,principle='independently compare the complete field note with every existing island and agree on the exact relation, matched island, category, and integer severity')

 @gl.public.write
 def chart_atlas(self,atlas_id:str,title:str,scope:str,categories:list[str])->None:
  key=ident(atlas_id); label=clean(title,120); boundary=clean(scope,500); vocab=[ident(item) for item in categories]
  if key in self.atlases or len(label)<5 or len(boundary)<30 or len(vocab)<2 or len(vocab)>6 or len(set(vocab))!=len(vocab): raise gl.vm.UserError('[EXPECTED] unique atlas, detailed scope, and closed categories required')
  self.atlases[key]=Atlas(gl.message.sender_address,label,boundary,json.dumps(vocab),'CHARTING','[]','[]')

 @gl.public.write
 def sound_observation(self,atlas_id:str,observation_id:str,title:str,note:str)->dict:
  key,atlas=self._atlas(atlas_id); oid=ident(observation_id); label=clean(title,100); body=clean(note,700); digest=hashlib.sha256(body.lower().encode()).hexdigest(); replay_key=key+'|'+digest
  if atlas.state!='CHARTING' or oid in self.observations or replay_key in self.attempted or len(label)<4 or len(body)<30: raise gl.vm.UserError('[EXPECTED] charting atlas, unique observation, and novel detailed note required')
  island_ids=json.loads(atlas.island_ids); existing=[]
  for island_id in island_ids:
   island=self.islands[island_id]; anchor=self.observations[island.anchor_observation_id]; existing.append({'id':island_id,'title':island.title,'anchor':anchor.note,'category':island.category,'severity':int(island.severity),'depth':int(island.depth)})
  verdict=self._sound(atlas.scope,json.loads(atlas.categories),existing,label,body); matched=verdict['matched_island']
  if verdict['relation']=='NEW':
   island_id=ident('ISLE-'+oid); self.islands[island_id]=Island(key,oid,label,verdict['category'],u256(verdict['severity']),u256(1)); island_ids.append(island_id); matched=island_id
  elif verdict['relation']=='DEEPENS':
   island=self.islands[matched]; island.depth=u256(int(island.depth)+1); island.severity=u256(max(int(island.severity),verdict['severity'])); self.islands[matched]=island
  self.observations[oid]=Observation(gl.message.sender_address,key,label,body,digest,verdict['relation'],matched,verdict['category'],u256(verdict['severity'])); self.attempted[replay_key]=True
  observation_ids=json.loads(atlas.observation_ids); observation_ids.append(oid); atlas.island_ids=json.dumps(island_ids); atlas.observation_ids=json.dumps(observation_ids); self.atlases[key]=atlas
  return {'observation_id':oid,'relation':verdict['relation'],'island_id':matched,'category':verdict['category'],'severity':verdict['severity'],'island_count':len(island_ids)}

 @gl.public.write
 def publish_map(self,atlas_id:str)->None:
  key,atlas=self._atlas(atlas_id)
  if addr(gl.message.sender_address)!=addr(atlas.curator) or atlas.state!='CHARTING' or len(json.loads(atlas.island_ids))<2: raise gl.vm.UserError('[EXPECTED] curator and at least two islands required')
  atlas.state='PUBLISHED'; self.atlases[key]=atlas

 @gl.public.view
 def get_atlas(self,atlas_id:str)->dict:
  key,atlas=self._atlas(atlas_id); islands=[]
  for island_id in json.loads(atlas.island_ids):
   item=self.islands[island_id]; islands.append({'id':island_id,'title':item.title,'category':item.category,'severity':int(item.severity),'depth':int(item.depth),'anchor_observation_id':item.anchor_observation_id})
  return {'id':key,'curator':atlas.curator.as_hex,'title':atlas.title,'scope':atlas.scope,'categories':json.loads(atlas.categories),'state':atlas.state,'islands':islands,'observation_ids':json.loads(atlas.observation_ids)}
 @gl.public.view
 def get_observation(self,observation_id:str)->dict:
  key=ident(observation_id)
  if key not in self.observations: raise gl.vm.UserError('[EXPECTED] observation not found')
  item=self.observations[key]
  return {'id':key,'reporter':item.reporter.as_hex,'atlas_id':item.atlas_id,'title':item.title,'note':item.note,'note_digest':item.note_digest,'relation':item.relation,'matched_island':item.matched_island,'category':item.category,'severity':int(item.severity)}
