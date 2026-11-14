import json,csv,html
from pathlib import Path
root=Path(__file__).resolve().parents[2];icons=json.loads((root/'assets/redraw/catalog.json').read_text())['icons']
pairs={
'fighter':('歼-20','F-22A'), 'bomber':('轰-6K','B-52H'), 'transport':('运-20','C-17A'), 'awacs':('空警-500','E-2D'), 'helicopter':('直-10','AH-64E'),
'uav_fixed':('翼龙Ⅰ','MQ-1C'), 'uav_male':('翼龙Ⅱ','MQ-9A'), 'uav_quad':('DJI Matrice 350 RTK','Skydio X10'), 'uav_vtol':('CW-25E（平台候选）','JUMP 20（平台候选）'),
'loitering':('CH-901','Switchblade 600'), 'cruise_missile':('长剑系列（具体型号待定）','BGM-109（具体批次待定）'), 'ballistic_missile':('东风-31AG（角色参考）','LGM-30G（角色参考）'),
'carrier':('福建舰（003）','福特级'), 'destroyer':('055型','阿利·伯克级 Flight III'), 'frigate':('054A型','佩里级（历史参考）'), 'patrol_boat':('056A型（角色参考）','Cyclone级（历史参考）'),
'missile_boat':('022型','待选公开参考；不强配不存在的直接对应型号'), 'usv':('JARI-USV（公开展示构型）','CUSV（公开展示构型）'), 'submarine':('039系列（公开外形待选）','弗吉尼亚级'), 'uuv':('潜龙三号','REMUS 600'),
'tank':('99A型','M1A2 SEP v3'), 'ifv':('04A型','M2A4 Bradley'), 'sp_howitzer':('PLZ-05','M109A7'), 'towed_gun':('PLL-01','M777'), 'mlrs':('PHL-03','M270A2'),
'sam':('红旗-9系列','Patriot（批次待定）'), 'truck':('解放 MV3系列','FMTV系列'), 'ugv':('中国公开轮式无人车（待选型）','MUTT（平台候选）'), 'robodog':('B2（平台外形候选）','Spot（平台外形候选）'),
'radar':('JY-27A（角色参考）','AN/TPS-80'), 'satellite':('高分一号','Landsat 9'), 'tanker':('运油-20','KC-46A'), 'ew_aircraft':('运-9电子战公开构型（待核对）','EA-37B'),
'recon_aircraft':('运-9侦察公开构型（待核对）','RC-135V/W'), 'transport_heli':('直-8L','CH-47F'), 'uav_heli':('AR500系列','MQ-8C'), 'hale_uav':('无侦-7','RQ-4B'),
'swarm':('多架中国四旋翼平台（具体平台待定）','多架美国四旋翼平台（具体平台待定）'), 'target_drone':('长空系列（具体型号待定）','BQM-167A'),
'amphibious':('075型','America级'), 'supply_ship':('901型','Supply级'), 'landing_craft':('726型','LCAC'), 'minesweeper':('081型','Avenger级'),
'glider':('海翼系列','Slocum系列'), 'research_vessel':('向阳红01（角色参考）','E/V Nautilus（角色参考）'), 'recon_vehicle':('09式侦察构型（待核对）','M1127 Stryker'),
'command_vehicle':('中国公开指挥车（待选型）','M1130 Stryker（角色参考）'), 'comm_vehicle':('中国公开通信车（待选型）','美国公开通信保障车（待选型）'),
'fuel_truck':('中国公开油料保障车（待选型）','M978A4'), 'ambulance':('中国公开越野救护车（待选型）','M997A3'), 'mortar':('PP-87（具体构型待核对）','M120'),
'spaa':('PGZ-09','M-SHORAD（角色参考）'), 'uav_flying_wing':('彩虹飞翼公开构型（待选型）','X-47B（试验机参考）'), 'uav_ucav':('攻击-11','X-47B（试验机参考）'),
'uav_tiltrotor':('中国公开倾转旋翼无人机（待选型）','V-247（设计构型参考）'), 'uav_hexa':('DJI Matrice 600（平台外形参考）','美国公开六旋翼平台（待选型）'),
'uav_fpv':('中国公开FPV平台（待选型）','美国公开FPV平台（待选型）'), 'uav_cargo':('中国公开物流无人机（待选型）','KARGO UAV（公开构型参考）'),
'uav_solar':('启明星50（试验构型参考）','Helios（历史试验参考）'), 'usv_large':('中国公开三体无人艇（待选型）','Sea Hunter'), 'usv_survey':('中国公开双体测量无人船（待选型）','美国公开双体测量无人船（待选型）'),
'uuv_xl':('中国公开超大型无人潜航器（待选型）','Orca XLUUV'), 'auv_portable':('中国公开便携AUV（待选型）','REMUS 100'),
'rov':('海龙系列（公开外形待选）','Jason ROV（角色参考）'), 'wave_glider':('中国公开波浪滑翔器（待选型）','Wave Glider'),
'ugv_logistics':('中国公开无人运输平台（待选型）','SMET/MUTT（平台参考）'), 'humanoid':('宇树 H1（平台外形候选）','Atlas（具体代次待定）'),
'asw_patrol':('运-8反潜公开构型（待核对）','P-8A'), 'carrier_fighter':('歼-15','F/A-18E/F'), 'attack_aircraft':('强-5（历史参考）','A-10C'),
'asw_heli':('直-20反潜公开构型（待核对）','MH-60R'), 'aew_heli':('直-18预警公开构型（待核对）','美国无直接对应现役预警直升机；待选参考'),
'elint_aircraft':('运-9电子侦察公开构型（待核对）','RC-135V/W'), 'ssbn':('094型（公开外形）','Ohio级'), 'elint_ship':('815A型','Victorious级（角色参考）'),
'lsd':('071型','San Antonio级'), 'aaa_gun':('PG-59（历史参考）','M167（历史参考）'), 'atgm_vehicle':('中国公开反坦克导弹车（待选型）','M1134 Stryker'),
'ashm':('鹰击系列（具体型号待定）','RGM-84（具体批次待定）'), 'aam':('霹雳系列（具体型号待定）','AIM-120（具体批次待定）'), 'arm':('中国公开反辐射导弹（待选型）','AGM-88系列'),
'ext_05_01':('长征五号','Falcon 9'), 'ext_05_02':('中国公开可回收验证构型（待选型）','Falcon 9一级'),
'ext_05_04':('中国空间站','ISS美国舱段（角色参考）'), 'ext_05_05':('神舟飞船','Crew Dragon'), 'ext_05_06':('天舟飞船','Cargo Dragon'),
'ext_05_09':('中国公开CubeSat（待指定任务）','美国公开CubeSat（待指定任务）'),
'ext_16_01':('复兴号（具体车型待定）','Acela（具体代次待定）'), 'ext_16_13':('中国公开滚装运输船（待选型）','美国公开滚装运输船（待选型）'),
'ext_16_15':('运-20救援任务公开涂装（平台参考）','C-130J（任务角色参考）'), 'ext_16_16':('运-12（平台参考）','Cessna 208（平台参考）')}
# Do not turn a known mismatch into a fictitious equipment model.
pairs['uav_coaxial']=('中国公开共轴无人直升机（待选型）','美国公开共轴无人直升机（待选型）')
pairs['uav_seaplane']=('中国公开水上无人机（待选型）','美国公开水上无人机（待选型）')
variant_families={'ruav_':'uav_heli','loiter_':'loitering','usv_':'usv','uuv_':'uuv','ugv_':'ugv'}
shared_cats={'指控信息','信息技术','云网基础','数据治理','人工智能','网络安全','组织协同','后勤保障','能源动力','医疗救援','海洋保障','无人作业','工业制造','试验仿真','环境感知','基础设施','设施','民用交通'}
shared_people={'operator','engineer','maintainer','analyst','expert_group','driver','trainee','user_group','civilian_engineer'}
rows=[]
for i in icons:
 k=i['key'];note='';cn=us='';family=None
 if k in {'uav_magnetic','uav_ew_vtol'}:
  strategy='中美平台外形＋专用载荷单独核对';cn='CW-25E（仅平台外形候选）';us='JUMP 20（仅平台外形候选）';note='不能据此声称候选平台已有该磁探／电子对抗配置；载荷沿用用户确认布局，国别适配另核对。'
 elif k in pairs:
  strategy='中美装备外形';cn,us=pairs[k];note='候选仅用于选型讨论；历史、试验、设计构型须在最终名称中明确，不表示两者性能或代际相当。'
 elif i['cat']=='人员' and k not in shared_people:
  strategy='中美人员服装／装备';cn='中国公开服装与随身装备（军种、年代待定）';us='美国公开服装与随身装备（军种、年代待定）';note='人员职能保持一致，按公开服装、头盔、携行具、工作台等外形区分。'
 elif any(k.startswith(p) for p in variant_families):
  family=next(v for p,v in variant_families.items() if k.startswith(p));strategy='同国平台复用＋任务载荷';cn,us=pairs.get(family,('待选中国公开平台','待选美国公开平台'));note='只继承平台外形参考；本图标专用载荷必须另找公开外形参考，不虚构对应型号。'
 elif i['cat'] in shared_cats or k in shared_people:
  strategy='通用共用';cn=us='共用现有通用资产';note='暂不强制制作两套；若后续指定真实品牌、型号、场站或服装，再单独做国别外形。'
 else:
  strategy='待选中美公开参考';cn=us='待选型';note='需先确认公开的代表外形；没有直接对应时保留通用版。'
 specific=strategy!='通用共用'
 rows.append({'key':k,'name':i['name'],'category':i['cat'],'strategy':strategy,'china_candidate':cn,'usa_candidate':us,'reference_status':'待核对公开外形与来源' if specific else '暂不分国别','verified':False,'china_source_url':None,'usa_source_url':None,'family_key':family,'note':note})
for r in rows:
 if r['strategy']=='通用共用': phase='共享资产，无需国别重绘'
 elif r['strategy']=='待选中美公开参考': phase='先选型，再排批次'
 elif r['strategy']=='中美人员服装／装备': phase='第4批：人员服装与携行装备'
 elif '载荷' in r['strategy']: phase='第2批：无人平台与任务载荷'
 elif r['category']=='空中': phase='第1批：典型航空平台'
 elif r['category'] in ['海上','陆地']: phase='第3批：舰船与地面平台'
 else: phase='第4批：专用设备与支援平台'
 r['production_phase']=phase
summary={s:sum(r['strategy']==s for r in rows) for s in sorted({r['strategy'] for r in rows})}
plan={'version':1,'total':len(rows),'scope':'全库外形对照清单初版；候选名称并非已核验的生产依据。','rules':['国别外形与红蓝涂装独立。','对拟制作的国别资产，先核对公开参考来源和至少正侧／俯视等关键轮廓。','不把不同代际或不同任务的装备声称为一一性能对应。','无法可靠对应的保留通用版；不虚构型号。'],'summary':summary,'icons':rows}
out=root/'assets/country-plan';(out/'catalog.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
with (out/'country-plan.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['编号','图标','类别','处理方式','中国候选','美国候选','参考状态','建议批次','已核验','说明'])
 for r in rows:w.writerow([r['key'],r['name'],r['category'],r['strategy'],r['china_candidate'],r['usa_candidate'],r['reference_status'],r['production_phase'],'否',r['note']])
assert len(rows)==len(icons) and len({r['key'] for r in rows})==len(icons)
print(json.dumps({'total':len(rows),'summary':summary,'named_candidates':sum(r['strategy']=='中美装备外形' for r in rows)},ensure_ascii=False))

template=(out/'template.html').read_text()
(out/'country-plan.html').write_text(template.replace('__DATA__',json.dumps(plan,ensure_ascii=False).replace('<','\\u003c')))
