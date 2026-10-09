import json,re,time
from pathlib import Path
from genlayer_py import create_account,create_client
from genlayer_py.chains import studionet
from genlayer_py.contracts import actions as contract_actions

def calldata_compat(method=None,args=None,kwargs=None):
 out={}
 if method is not None: out['method']=method
 if args: out['args']=args
 if kwargs: out['kwargs']=kwargs
 return out
contract_actions.make_calldata_object=calldata_compat

ROOT=Path(__file__).parents[1]; ENV=(ROOT.parents[3]/'accounts.env').read_text(); ADDRESS=json.loads((ROOT/'deployment.json').read_text())['contractAddress']
def owner(): return create_account(account_private_key=re.search(r'^ACCOUNT_2_GENLAYER_PRIVATE_KEY\s*=\s*"?([^"\r\n]+)',ENV,re.M).group(1).strip())
def client(acct): return create_client(chain=studionet,account=acct)
def wait(c,tx,expect='SUCCESS'):
 receipt=c.wait_for_transaction_receipt(transaction_hash=tx,wait_until='finalized',retries=180,interval=5000,full_transaction=True); leaders=receipt.get('consensus_data',{}).get('leader_receipt')or[]; leaders=[leaders] if isinstance(leaders,dict) else leaders; executions=[str(row.get('execution_result','')).upper() for row in leaders]; assert receipt.get('result_name')=='MAJORITY_AGREE' and expect in executions; return receipt,executions
def write(c,name,args,expect='SUCCESS'):
 tx=c.write_contract(address=ADDRESS,function_name=name,args=args); print(name+'_tx='+str(tx),flush=True); _,executions=wait(c,tx,expect); return str(tx),executions

curator=owner(); cc=client(curator); scouts=[client(create_account()) for _ in range(4)]; stamp=str(int(time.time())); aid='ATLAS-'+stamp; scope='Map concrete operational risks affecting visitors, staff, access, safety, and continuity at the shared public archive.'; first='The uncovered east queue has no shade or water point, creating sustained heat exposure for visitors waiting at midday.'; second='The current translated visitor guide omits the emergency exit route, leaving non-English readers without evacuation directions.'; deeper='The same east queue uses dark paving that stores afternoon heat, so exposure continues after direct sun has moved away.'; tx={}
tx['chart'],_=write(cc,'chart_atlas',[aid,'Visitor experience risk map',scope,['SAFETY','ACCESS','CONTINUITY']]); tx['heat'],_=write(scouts[0],'sound_observation',[aid,'HEAT-'+stamp,'Heat refuge missing at the east queue',first]); tx['language'],_=write(scouts[1],'sound_observation',[aid,'LANGUAGE-'+stamp,'Emergency route unavailable in translated guide',second]); tx['depth'],_=write(scouts[2],'sound_observation',[aid,'PAVING-'+stamp,'Paving extends the queue heat hazard',deeper]); before=cc.read_contract(address=ADDRESS,function_name='get_atlas',args=[aid]); observations=[cc.read_contract(address=ADDRESS,function_name='get_observation',args=[key]) for key in before['observation_ids']]; assert [item['relation'] for item in observations]==['NEW','NEW','DEEPENS'] and len(before['islands'])==2 and max(item['depth'] for item in before['islands'])==2
replay_tx=scouts[3].write_contract(address=ADDRESS,function_name='sound_observation',args=[aid,'REPLAY-'+stamp,'Copied heat note','  the uncovered east queue has no shade or water point, creating sustained heat exposure for visitors waiting at midday.  ']); tx['replay']=str(replay_tx); replay_receipt,replay_execution=wait(scouts[3],replay_tx,'ERROR'); after=cc.read_contract(address=ADDRESS,function_name='get_atlas',args=[aid]); assert after['islands']==before['islands'] and after['observation_ids']==before['observation_ids']; tx['publish'],_=write(cc,'publish_map',[aid]); final=cc.read_contract(address=ADDRESS,function_name='get_atlas',args=[aid]); assert final['state']=='PUBLISHED'
proof={'atlasId':aid,'contract':ADDRESS,'transactions':tx,'observations':[{'id':item['id'],'relation':item['relation'],'island':item['matched_island'],'category':item['category'],'severity':item['severity']} for item in observations],'map':{'state':final['state'],'islandCount':len(final['islands']),'islands':final['islands']},'normalizedReplay':{'consensus':replay_receipt.get('result_name'),'execution':replay_execution,'islandsUnchanged':after['islands']==before['islands'],'observationsUnchanged':after['observation_ids']==before['observation_ids']},'fixtureDisclosure':'Field notes and wallets are operator-controlled fixtures used to prove semantic set mutation and cross-wallet normalized replay rejection.'}; (ROOT/'evidence').mkdir(exist_ok=True); (ROOT/'evidence'/'live-run.json').write_text(json.dumps(proof,indent=2)+'\n'); print(json.dumps(proof,indent=2),flush=True)
