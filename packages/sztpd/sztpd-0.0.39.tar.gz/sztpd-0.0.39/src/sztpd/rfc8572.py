# Copyright (c) 2019-2025 Watsen Networks. All Rights Reserved.

from __future__ import annotations
_AW='Unrecognized error-tag: '
_AV='partial-operation'
_AU='operation-failed'
_AT='rollback-failed'
_AS='data-exists'
_AR='resource-denied'
_AQ='lock-denied'
_AP='unknown-namespace'
_AO='bad-element'
_AN='unknown-attribute'
_AM='missing-attribute'
_AL='exception-thrown'
_AK='function-details'
_AJ='from-device'
_AI='source-ip-address'
_AH='"ietf-sztp-bootstrap-server:input" is missing.'
_AG='ssl_object'
_AF='/ietf-sztp-bootstrap-server:report-progress'
_AE='Resource does not exist.'
_AD='Requested resource does not exist.'
_AC='%Y-%m-%dT%H:%M:%SZ'
_AB='2019-04-30'
_AA='urn:ietf:params:xml:ns:yang:ietf-yang-types'
_A9='ietf-yang-types'
_A8='module-set-id'
_A7='ietf-yang-library:modules-state'
_A6='application/yang-data+xml'
_A5='webhooks'
_A4='callout-type'
_A3='access-denied'
_A2='bad-attribute'
_A1='/ietf-sztp-bootstrap-server:get-bootstrapping-data'
_A0='Parent node does not exist.'
_z='Resource can not be modified.'
_y='functions'
_x='/yangcore:dynamic-callouts/dynamic-callout='
_w='/sztpd:devices/device='
_v='2024-10-10'
_u='2013-07-15'
_t='webhook'
_s='exited-normally'
_r='operation-not-supported'
_q='opaque'
_p='rpc-supported'
_o='data-missing'
_n='Unable to parse "input" document: '
_m='sztpd:device'
_l='import'
_k='Content-Type'
_j=False
_i='plugin'
_h='application/yang-data+json'
_g='malformed-message'
_f='function'
_e='implement'
_d='function-results'
_c='application'
_b='unknown-element'
_a=True
_Z='call-function'
_Y='invalid-value'
_X='ietf-sztp-bootstrap-server:input'
_W='path'
_V='method'
_U='source-ip'
_T='serial-number'
_S='conformance-type'
_R='namespace'
_Q='revision'
_P='error-tag'
_O='request'
_N='timestamp'
_M='error'
_L='protocol'
_K='text/plain'
_J='yangcore:dynamic-callout'
_I='ietf-restconf:errors'
_H='+'
_G='name'
_F='return-code'
_E='error-returned'
_D='/'
_C=None
_B='handling'
_A='response'
import importlib.resources as importlib_resources,urllib.parse,datetime,asyncio,base64,json,os,aiohttp,yangson,basicauth
from aiohttp import web
from certvalidator import CertificateValidator,ValidationContext,PathBuildingError
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from passlib.hash import sha256_crypt
from pyasn1.type import univ
from pyasn1.codec.der.encoder import encode as encode_der
from pyasn1.codec.der.decoder import decode as der_decoder
from pyasn1_modules import rfc5652
from yangcore import utils
from yangcore.native import Read
from yangcore.dal import NodeNotFound
from yangcore.rcsvr import RestconfServer
from yangcore.handler import RouteHandler
from yangcore.yl import yl_8525_to_7895
from sztpd.yl import sztpd_rfc8572_yang_library
class RFC8572ViewHandler(RouteHandler):
	len_prefix_running=len(RestconfServer.root+'/ds/ietf-datastores:running');len_prefix_operational=len(RestconfServer.root+'/ds/ietf-datastores:operational');len_prefix_operations=len(RestconfServer.root+'/operations');id_ct_sztpConveyedInfoXML=rfc5652._buildOid(1,2,840,113549,1,9,16,1,42);id_ct_sztpConveyedInfoJSON=rfc5652._buildOid(1,2,840,113549,1,9,16,1,43);supported_media_types=_h,_A6;yl4errors={_A7:{_A8:'TBD','module':[{_G:_A9,_Q:_u,_R:_AA,_S:_l},{_G:'ietf-restconf',_Q:'2017-01-26',_R:'urn:ietf:params:xml:ns:yang:ietf-restconf',_S:_e},{_G:'ietf-netconf-acm',_Q:'2018-02-14',_R:'urn:ietf:params:xml:ns:yang:ietf-netconf-acm',_S:_l},{_G:'ietf-sztp-bootstrap-server',_Q:_AB,_R:'urn:ietf:params:xml:ns:yang:ietf-sztp-bootstrap-server',_S:_e},{_G:'ietf-yang-structure-ext',_Q:'2020-06-17',_R:'urn:ietf:params:xml:ns:yang:ietf-yang-structure-ext',_S:_e},{_G:'ietf-ztp-types',_Q:_v,_R:'urn:ietf:params:xml:ns:yang:ietf-ztp-types',_S:_e},{_G:'ietf-sztp-csr',_Q:_v,_R:'urn:ietf:params:xml:ns:yang:ietf-sztp-csr',_S:_e},{_G:'ietf-crypto-types',_Q:_v,_R:'urn:ietf:params:xml:ns:yang:ietf-crypto-types',_S:_e}]}};yl4conveyedinfo={_A7:{_A8:'TBD','module':[{_G:_A9,_Q:_u,_R:_AA,_S:_l},{_G:'ietf-inet-types',_Q:_u,_R:'urn:ietf:params:xml:ns:yang:ietf-inet-types',_S:_l},{_G:'ietf-sztp-conveyed-info',_Q:_AB,_R:'urn:ietf:params:xml:ns:yang:ietf-sztp-conveyed-info',_S:_e}]}}
	def __init__(A,dal,yl_obj,nvh):E='sztpd';D='yang';A.dal=dal;A.nvh=nvh;B=importlib_resources.files('yangcore')/D;C=importlib_resources.files(E)/D;F=yl_8525_to_7895(yl_obj);A.dm=yangson.DataModel(json.dumps(F),[B,C]);A.dm4conveyedinfo=yangson.DataModel(json.dumps(A.yl4conveyedinfo),[B,C]);G=importlib_resources.files(E)/'yang4errors';A.dm4errors=yangson.DataModel(json.dumps(A.yl4errors),[G,B,C])
	async def _insert_bootstrapping_log_record(C,device_id,bootstrapping_log_record):
		A=bootstrapping_log_record;D=_w+device_id[0]+'/bootstrapping-log';F={'sztpd:bootstrapping-log-record':A};await C.dal.handle_post_opstate_request(D,F)
		try:G=await C.dal.handle_get_config_request('/yangcore:preferences/outbound-interactions/sztpd:relay-bootstrapping-log-record-callout',{})
		except NodeNotFound:return
		E=G['sztpd:relay-bootstrapping-log-record-callout'];D=_x+E;B=await C.dal.handle_get_config_request(D,{});B=B[_J][0];assert E==B[_G];H=B[_Z][_i];I=B[_Z][_f];A[_N]=A[_N].strftime(_AC);A.pop('parent_id');J={'bootstrapping-log-record':A};K=_C;L=await C.nvh.plugins[H][_y][I](J,K);assert L is _C
	async def handle_get_restconf_root(D,request):
		C=request;J=_D;F=await D._check_auth(C,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=C.remote;B[_A]={};B[_O]={_V:C.method,_W:C.path};E,K=utils.check_http_headers(C,D.supported_media_types,accept_required=_a)
		if isinstance(E,web.Response):A=E;L=K;B[_A][_F]=A.status;B[_A][_E]=L;await D._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;I=utils.Encoding[H.rsplit(_H,1)[1].upper()];A=web.Response(status=200);A.content_type=H
		if I==utils.Encoding.JSON:A.text='{\n    "ietf-restconf:restconf" : {\n        "data" : {},\n        "operations" : {},\n        "yang-library-version" : "2019-01-04"\n    }\n}\n'
		else:assert I==utils.Encoding.XML;A.text='<restconf xmlns="urn:ietf:params:xml:ns:yang:ietf-restconf">\n    <data/>\n    <operations/>\n    <yang-library-version>2016-06-21</yang-library-version>\n</restconf>\n'
		B[_A][_F]=A.status;await D._insert_bootstrapping_log_record(G,B);return A
	async def handle_get_yang_library_version(D,request):
		C=request;J=_D;F=await D._check_auth(C,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=C.remote;B[_A]={};B[_O]={_V:C.method,_W:C.path};E,K=utils.check_http_headers(C,D.supported_media_types,accept_required=_a)
		if isinstance(E,web.Response):A=E;L=K;B[_A][_F]=A.status;B[_A][_E]=L;await D._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;I=utils.Encoding[H.rsplit(_H,1)[1].upper()];A=web.Response(status=200);A.content_type=H
		if I==utils.Encoding.JSON:A.text='{\n  "ietf-restconf:yang-library-version" : "2019-01-04"\n}'
		else:assert I==utils.Encoding.XML;A.text='<yang-library-version xmlns="urn:ietf:params:xml:ns:'+'yang:ietf-restconf">2019-01-04</yang-library-version>'
		B[_A][_F]=A.status;await D._insert_bootstrapping_log_record(G,B);return A
	async def handle_get_opstate_request(C,request):
		D=request;F=D.path[C.len_prefix_operational:];F=_D;G=await C._check_auth(D,F)
		if isinstance(G,web.Response):A=G;return A
		H=G;B={};B[_T]=H[0];B[_N]=datetime.datetime.utcnow();B[_U]=D.remote;B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_a)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(H,B);return A
		assert isinstance(E,str);I=E;assert I!=_K;J=utils.Encoding[I.rsplit(_H,1)[1].upper()]
		if F in('',_D,'/ietf-yang-library:yang-library'):A=web.Response(status=200);A.content_type=_h;A.text=json.dumps(sztpd_rfc8572_yang_library())
		else:A=web.Response(status=404);A.content_type=I;J=utils.Encoding[A.content_type.rsplit(_H,1)[1].upper()];K=utils.gen_rc_errors(_L,_b,error_message=_AD);N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(K,J,C.dm4errors,N);B[_A][_E]=K
		B[_A][_F]=A.status;await C._insert_bootstrapping_log_record(H,B);return A
	async def handle_get_config_request(C,request):
		D=request;I=D.path[C.len_prefix_running:];F=await C._check_auth(D,I)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=D.remote;B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_a)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;J=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if I in('',_D):A=web.Response(status=204)
		else:A=web.Response(status=404);A.content_type=H;J=utils.Encoding[A.content_type.rsplit(_H,1)[1].upper()];K=utils.gen_rc_errors(_L,_b,error_message=_AD);N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(K,J,C.dm4errors,N);B[_A][_E]=K
		B[_A][_F]=A.status;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_post_config_request(C,request):
		D=request;J=D.path[C.len_prefix_running:];F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=D.remote;B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_j)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;K=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if J in('',_D):A=web.Response(status=400);I=utils.gen_rc_errors(_c,_Y,error_message=_z)
		else:A=web.Response(status=404);I=utils.gen_rc_errors(_L,_b,error_message=_A0)
		A.content_type=H;K=utils.Encoding[A.content_type.rsplit(_H,1)[1]].upper();N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(I,K,C.dm4errors,N);B[_A][_F]=A.status;B[_A][_E]=I;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_put_config_request(C,request):
		D=request;J=D.path[C.len_prefix_running:];F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=D.remote;B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_j)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;K=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if J in('',_D):A=web.Response(status=400);I=utils.gen_rc_errors(_c,_Y,error_message=_z)
		else:A=web.Response(status=404);I=utils.gen_rc_errors(_L,_b,error_message=_A0)
		A.content_type=H;K=utils.Encoding[A.content_type.rsplit(_H,1)[1]].upper();N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(I,K,C.dm4errors,N);B[_A][_F]=A.status;B[_A][_E]=I;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_delete_config_request(C,request):
		D=request;L=D.path[C.len_prefix_running:];G=await C._check_auth(D,L)
		if isinstance(G,web.Response):A=G;return A
		H=G;B={};B[_T]=H[0];B[_N]=datetime.datetime.utcnow();B[_U]=D.remote;B[_A]={};B[_O]={_V:D.method,_W:D.path};E,M=utils.check_http_headers(D,C.supported_media_types,accept_required=_j)
		if isinstance(E,web.Response):A=E;N=M;B[_A][_F]=A.status;B[_A][_E]=N;await C._insert_bootstrapping_log_record(H,B);return A
		assert isinstance(E,str);I=E
		if I==_K:J=_C
		else:J=utils.Encoding[I.rsplit(_H,1)[1].upper()]
		if L in('',_D):A=web.Response(status=400);F=_z;K=utils.gen_rc_errors(_c,_Y,error_message=F)
		else:A=web.Response(status=404);F=_A0;K=utils.gen_rc_errors(_L,_b,error_message=F)
		A.content_type=I
		if J is _C:A.text=F
		else:O=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(K,J,C.dm4errors,O)
		B[_A][_F]=A.status;B[_A][_E]=K;await C._insert_bootstrapping_log_record(H,B);return A
	async def handle_action_request(C,request):
		D=request;J=D.path[C.len_prefix_operational:];F=await C._check_auth(D,J)
		if isinstance(F,web.Response):A=F;return A
		G=F;B={};B[_T]=G[0];B[_N]=datetime.datetime.utcnow();B[_U]=D.remote;B[_A]={};B[_O]={_V:D.method,_W:D.path};E,L=utils.check_http_headers(D,C.supported_media_types,accept_required=_j)
		if isinstance(E,web.Response):A=E;M=L;B[_A][_F]=A.status;B[_A][_E]=M;await C._insert_bootstrapping_log_record(G,B);return A
		assert isinstance(E,str);H=E;assert H!=_K;K=utils.Encoding[H.rsplit(_H,1)[1].upper()]
		if J in('',_D):A=web.Response(status=400);I=utils.gen_rc_errors(_c,_Y,error_message='Resource does not support action.')
		else:A=web.Response(status=404);I=utils.gen_rc_errors(_L,_b,error_message=_AE)
		A.content_type=H;K=utils.Encoding[A.content_type.rsplit(_H,1)[1]].upper();N=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(I,K,C.dm4errors,N);B[_A][_F]=A.status;B[_A][_E]=I;await C._insert_bootstrapping_log_record(G,B);return A
	async def handle_rpc_request(D,request):
		J='sleep';B=request;F=B.path[D.len_prefix_operations:];G=await D._check_auth(B,F)
		if isinstance(G,web.Response):C=G;return C
		E=G;A={};A[_T]=E[0];A[_N]=datetime.datetime.utcnow();A[_U]=B.remote;A[_A]={};A[_O]={_V:B.method,_W:B.path}
		if F==_A1:
			async with D.nvh.fifolock(Read):
				if os.environ.get('SZTPD_INIT_MODE')and J in B.query:await asyncio.sleep(int(B.query[J]))
				C=await D._handle_get_bootstrapping_data_rpc(E,B,A);A[_A][_F]=C.status;await D._insert_bootstrapping_log_record(E,A)
			return C
		if F==_AF:C=await D._handle_report_progress_rpc(E,B,A);A[_A][_F]=C.status;await D._insert_bootstrapping_log_record(E,A);return C
		if F in(''or _D):C=web.Response(status=400);H=_AE
		else:C=web.Response(status=404);H='Unrecognized RPC.'
		I,K=utils.format_resp_and_msg(C,H,_A2,B,D.supported_media_types);A[_A][_F]=I.status;A[_A][_E]=K;await D._insert_bootstrapping_log_record(E,A);return I
	async def _check_auth(A,request,data_path):
		i='num-times-accessed';h='central-truststore-reference';g='sztpd:device-type';f='identity-certificates';e='activation-code';d='X-Client-Cert';T='verification';S='device-type';O='sbi-access-stats';K='lifecycle-statistics';I='comment';H='failure';E='outcome';C=request;assert data_path[0]==_D
		def F(request,supported_media_types):
			E=supported_media_types;D='Accept';C=request;B=web.Response(status=401)
			if D in C.headers and any(C.headers[D]==A for A in E):B.content_type=C.headers[D]
			elif _k in C.headers and any(C.headers[_k]==A for A in E):B.content_type=C.headers[_k]
			else:B.content_type=_K
			if B.content_type!=_K:F=utils.Encoding[B.content_type.rsplit(_H,1)[1].upper()];G=utils.gen_rc_errors(_L,_A3);H=A.dm4errors.get_schema_node(_D);B.text=utils.obj_to_encoded_str(G,F,A.dm4errors,H)
			return B
		B={};B[_N]=datetime.datetime.utcnow();B[_U]=C.remote;B['source-proxies']=list(C.forwarded);B['host']=C.host;B[_V]=C.method;B[_W]=C.path;J=set();L=_C;M=C.transport.get_extra_info('peercert')
		if M is not _C:N=M['subject'][-1][0][1];J.add(N)
		elif C.headers.get(d)is not _C:j=C.headers.get(d);U=bytes(urllib.parse.unquote(j),'utf-8');L=x509.load_pem_x509_certificate(U,default_backend());k=L.subject;N=k.get_attributes_for_oid(x509.ObjectIdentifier('2.5.4.5'))[0].value;J.add(N)
		P=_C;V=_C;Q=C.headers.get('AUTHORIZATION')
		if Q is not _C:P,V=basicauth.decode(Q);J.add(P)
		if len(J)==0:B[E]=H;B[I]='Device provided no identification credentials.';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		if len(J)!=1:B[E]=H;B[I]='Device provided mismatched authentication credentials ('+N+' != '+P+').';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		G=J.pop();D=_C;W=_w+G
		try:D=await A.dal.handle_get_opstate_request(W,{})
		except NodeNotFound:B[E]=H;B[I]='Device "'+G+'" not found for any tenant.';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		l=_C;assert D is not _C;assert _m in D;D=D[_m][0]
		if e in D:
			if Q is _C:B[E]=H;B[I]='Activation code required but none passed for serial number '+G;await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
			X=D[e];assert X.startswith('$5$')
			if not sha256_crypt.verify(V,X):B[E]=H;B[I]='Activation code mismatch for serial number '+G;await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		assert S in D;m='/sztpd:device-types/device-type='+D[S];Y=await A.dal.handle_get_opstate_request(m,{})
		if f in Y[g][0]:
			if M is _C and L is _C:B[E]=H;B[I]='Client cert required but none passed for serial number '+G;await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
			if M:Z=C.transport.get_extra_info(_AG);assert Z is not _C;a=Z.getpeercert(_a)
			else:assert L is not _C;a=U
			R=Y[g][0][f];assert T in R;assert h in R[T];b=R[T][h];n='/ietf-truststore:truststore/certificate-bags/certificate-bag='+b['certificate-bag']+'/certificate='+b['certificate'];o=await A.dal.handle_get_config_request(n,{});p=o['ietf-truststore:certificate'][0]['cert-data'];q=base64.b64decode(p);r,s=der_decoder(q,asn1Spec=rfc5652.ContentInfo());assert not s;t=utils.degenerate_cms_obj_to_ders(r);u=ValidationContext(trust_roots=t);v=CertificateValidator(a,validation_context=u)
			try:v._validate_path()
			except PathBuildingError:B[E]=H;B[I]="Client cert for serial number '"+G+"' does not validate using trust anchors specified by device-type '"+D[S]+"'";await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);return F(C,A.supported_media_types)
		B[E]='success';await utils.insert_audit_log_record(A.dal,A.nvh.plugins,B);w=W+'/lifecycle-statistics';c=datetime.datetime.utcnow().strftime(_AC)
		if D[K][O][i]==0:D[K][O]['first-accessed']=c
		D[K][O]['last-accessed']=c;D[K][O][i]+=1;await A.dal.handle_put_opstate_request(w,D[K]);return G,l
	async def _handle_get_bootstrapping_data_rpc(B,device_id,request,bootstrapping_log_record):
		AO='ietf-sztp-bootstrap-server:output';AN='content';AM='contentType';AL='sztpd:configuration';AK='sztpd:script';AJ='/sztpd:conveyed-information/scripts/script=';AI='hash-value';AH='hash-algorithm';AG='os-version';AF='os-name';AE='address';AD='referenced-definition';AC='match-criteria';AB='matched-response';A4=device_id;A3='post-configuration-script';A2='configuration';A1='pre-configuration-script';A0='trust-anchor';z='port';y='bootstrap-server';x='ietf-sztp-conveyed-info:redirect-information';w='value';v='response-manager';n='image-verification';m='download-uri';l='boot-image';k='via-onboarding-response';j='via-redirect-response';i='reference';h='selected-response';c='key';Z=request;V='ietf-sztp-conveyed-info:onboarding-information';N='via-dynamic-callout';J='managed-response';I='response-details';E='get-bootstrapping-data';D='conveyed-information';C=bootstrapping_log_record;d,AP=utils.check_http_headers(Z,B.supported_media_types,accept_required=_a)
		if isinstance(d,web.Response):A=d;AQ=AP;C[_A][_F]=A.status;C[_A][_E]=AQ;return A
		assert isinstance(d,str);O=d;assert O!=_K;Q=utils.Encoding[O.rsplit(_H,1)[1].upper()];K=_C
		if Z.body_exists:
			AR=await Z.text();AS=utils.Encoding[Z.headers[_k].rsplit(_H,1)[1].upper()];F=B.dm.get_schema_node(_A1)
			try:K=utils.encoded_str_to_obj(AR,AS,B.dm,F)
			except utils.TranscodingError as W:A=web.Response(status=400);o=_n+str(W);A.content_type=O;G=utils.gen_rc_errors(_L,_g,error_message=o);F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,Q,B.dm4errors,F);C[_A][_E]=G;return A
			if not _X in K:
				A=web.Response(status=400)
				if not _X in K:o=_n+_AH
				A.content_type=O;G=utils.gen_rc_errors(_L,_g,error_message=o);F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,Q,B.dm4errors,F);C[_A][_E]=G;return A
		if K is _C:C[_O]['body']=[_C]
		else:C[_O]['body']=K
		C[_B]={};C[_B][E]={};A5=_C
		if K:
			try:A5=K[_X]
			except KeyError:A=web.Response(status=400);A.content_type=_h;G=utils.gen_rc_errors(_L,_Y,error_message='RPC "input" node missing.');A.text=utils.enc_rc_errors('json',G);return A
			F=B.dm.get_schema_node('/ietf-sztp-bootstrap-server:get-bootstrapping-data/input')
			try:F.from_raw(A5)
			except yangson.exceptions.RawMemberError as W:A=web.Response(status=400);A.content_type=_h;G=utils.gen_rc_errors(_L,_Y,error_message='RPC "input" node fails YANG validation here: '+str(W));A.text=utils.enc_rc_errors('json',G);return A
		AT=_w+A4[0];S=await B.dal.handle_get_config_request(AT,{});assert S is not _C;assert _m in S;S=S[_m][0]
		if v not in S or AB not in S[v]:A=web.Response(status=404);A.content_type=O;G=utils.gen_rc_errors(_c,_o,error_message='No responses configured.');F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,Q,B.dm4errors,F);C[_A][_E]=G;C[_B][E][h]='no-responses-configured';return A
		H=_C
		for e in S[v][AB]:
			if not AC in e:H=e;break
			if K is _C:continue
			for P in e[AC]['match']:
				if P[c]not in K[_X]:break
				if'present'in P:
					if'not'in P:
						if P[c]in K[_X]:break
					elif P[c]not in K[_X]:break
				elif w in P:
					if'not'in P:
						if P[w]==K[_X][P[c]]:break
					elif P[w]!=K[_X][P[c]]:break
				else:raise NotImplementedError("Unrecognized 'match' expression.")
			else:H=e;break
		if H is _C or'none'in H[_A]:
			if H is _C:C[_B][E][h]='no-match-found'
			else:C[_B][E][h]=H[_G]+" (explicit 'none')"
			A=web.Response(status=404);A.content_type=O;G=utils.gen_rc_errors(_c,_o,error_message='No matching responses configured.');F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,Q,B.dm4errors,F);C[_A][_E]=G;return A
		C[_B][E][h]=H[_G];C[_B][E][I]={J:{}}
		if D in H[_A]:
			C[_B][E][I][J]={D:{}};M={}
			if N in H[_A][D]:
				C[_B][E][I][J][D]={N:{}};assert i in H[_A][D][N];p=H[_A][D][N][i];C[_B][E][I][J][D][N][_G]=p;q=await B.dal.handle_get_config_request(_x+p,{});T=q[_J][0];assert p==T[_G];C[_B][E][I][J][D][N][_p]=T[_p];f={};f[_T]=A4[0];f[_AI]=Z.remote
				if K:f[_AJ]=K
				if _Z in T:
					C[_B][E][I][J][D][N][_A4]=_f;A6=T[_Z][_i];A7=T[_Z][_f];C[_B][E][I][J][D][N][_AK]={_i:A6,_f:A7};C[_B][E][I][J][D][N][_d]={}
					if _q in T:A8=T[_q]
					else:A8=_C
					L=_C
					try:L=await B.nvh.plugins[A6][_y][A7](f,A8)
					except Exception as W:C[_B][E][I][J][D][N][_d][_AL]=str(W);A=web.Response(status=500);A.content_type=O;G=utils.gen_rc_errors(_c,_r,error_message='Server '+'encountered an error while trying to generate '+'a response: '+str(W));F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,Q,B.dm4errors,F);C[_A][_E]=G;return A
					assert L and isinstance(L,dict)
					if _I in L:
						assert len(L[_I][_M])==1
						if any(A==L[_I][_M][0][_P]for A in(_Y,'too-big',_AM,_A2,_AN,_AO,_b,_AP,_g)):A=web.Response(status=400)
						elif any(A==L[_I][_M][0][_P]for A in _A3):A=web.Response(status=403)
						elif any(A==L[_I][_M][0][_P]for A in('in-use',_AQ,_AR,_AS,_o)):A=web.Response(status=409)
						elif any(A==L[_I][_M][0][_P]for A in(_AT,_AU,_AV)):A=web.Response(status=500)
						elif any(A==L[_I][_M][0][_P]for A in _r):A=web.Response(status=501)
						else:raise NotImplementedError(_AW+L[_I][_M][0][_P])
						A.content_type=O;G=L;F=B.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(G,Q,B.dm4errors,F);C[_A][_E]=L;C[_B][E][I][J][D][N][_d][_s]='Returning an RPC-error provided by function (NOTE: RPC-error '+'!= exception, hence a normal exit).';return A
					C[_B][E][I][J][D][N][_d][_s]='Returning conveyed information provided by function.'
				elif _A5 in q[_J][0]:C[_B][E][I][J][D][N][_A4]=_t;raise NotImplementedError('webhooks were disabled!')
				else:raise NotImplementedError('unhandled dynamic callout type: '+str(q[_J][0]))
				M=L[D]
			elif j in H[_A][D]:
				C[_B][E][I][J][D]={j:{}};M[x]={};M[x][y]=[];a=H[_A][D][j][i];C[_B][E][I][J][D][j]={AD:a};r=await B.dal.handle_get_config_request('/sztpd:responses/redirect-response='+a,{})
				for AU in r['sztpd:redirect-response'][0]['redirect-information'][y]:
					U=await B.dal.handle_get_config_request('/sztpd:conveyed-information/bootstrap-servers/bootstrap-server='+AU,{});U=U['sztpd:bootstrap-server'][0];g={};g[AE]=U[AE]
					if z in U:g[z]=U[z]
					if A0 in U:g[A0]=U[A0]
					M[x][y].append(g)
			elif k in H[_A][D]:
				C[_B][E][I][J][D]={k:{}};M[V]={};a=H[_A][D][k][i];C[_B][E][I][J][D][k]={AD:a};r=await B.dal.handle_get_config_request('/sztpd:responses/onboarding-response='+a,{});R=r['sztpd:onboarding-response'][0]['onboarding-information']
				if l in R:
					AV=R[l];AW=await B.dal.handle_get_config_request('/sztpd:conveyed-information/boot-images/boot-image='+AV,{});X=AW['sztpd:boot-image'][0];M[V][l]={};Y=M[V][l];Y[AF]=X[AF];Y[AG]=X[AG]
					if m in X:
						Y[m]=[]
						for AX in X[m]:Y[m].append(AX)
					if n in X:
						Y[n]=[]
						for A9 in X[n]:s={};s[AH]=A9[AH];s[AI]=A9[AI];Y[n].append(s)
				if A1 in R:AY=R[A1];AZ=await B.dal.handle_get_config_request(AJ+AY,{});M[V][A1]=AZ[AK][0]['code']
				if A2 in R:Aa=R[A2];AA=await B.dal.handle_get_config_request('/sztpd:conveyed-information/configurations/configuration='+Aa,{});M[V]['configuration-handling']=AA[AL][0][_B];M[V][A2]=AA[AL][0]['config-data']
				if A3 in R:Ab=R[A3];Ac=await B.dal.handle_get_config_request(AJ+Ab,{});M[V][A3]=Ac[AK][0]['code']
		else:raise NotImplementedError('unhandled response type: '+str(H[_A]))
		b=rfc5652.ContentInfo()
		if O==_h:b[AM]=B.id_ct_sztpConveyedInfoJSON;b[AN]=encode_der(json.dumps(M,indent=2),asn1Spec=univ.OctetString())
		else:assert O==_A6;b[AM]=B.id_ct_sztpConveyedInfoXML;F=B.dm4conveyedinfo.get_schema_node(_D);assert F;Ad=utils.obj_to_encoded_str(M,Q,B.dm4conveyedinfo,F,strip_wrapper=_a);b[AN]=encode_der(Ad,asn1Spec=univ.OctetString())
		Ae=encode_der(b,rfc5652.ContentInfo());t=base64.b64encode(Ae).decode('ASCII');Af=base64.b64decode(t);Ag=base64.b64encode(Af).decode('ASCII');assert t==Ag;u={};u[AO]={};u[AO][D]=t;A=web.Response(status=200);A.content_type=O;F=B.dm.get_schema_node(_A1);A.text=utils.obj_to_encoded_str(u,Q,B.dm,F);return A
	async def _handle_report_progress_rpc(C,device_id,request,bootstrapping_log_record):
		f='remote-port';e='webhook-results';d='sztpd:relay-progress-report-callout';X='tcp-client-parameters';U='http';K=request;G='dynamic-callout';E='report-progress';B=bootstrapping_log_record;S,g=utils.check_http_headers(K,C.supported_media_types,accept_required=_j)
		if isinstance(S,web.Response):A=S;h=g;B[_A][_F]=A.status;B[_A][_E]=h;return A
		assert isinstance(S,str);J=S
		if J==_K:L=_K
		else:i=J.rsplit(_H,1)[1].upper();L=utils.Encoding[i]
		if not K.body_exists:
			M='RPC "input" node missing (required for "report-progress").';A=web.Response(status=400);A.content_type=J
			if A.content_type==_K:A.text=M
			else:F=utils.gen_rc_errors(_L,_Y,error_message=M);H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H)
			B[_A][_E]=A.text;return A
		j=utils.Encoding[K.headers[_k].rsplit(_H,1)[1].upper()];k=await K.text();H=C.dm.get_schema_node(_AF)
		try:Q=utils.encoded_str_to_obj(k,j,C.dm,H)
		except utils.TranscodingError as N:A=web.Response(status=400);M=_n+str(N);A.content_type=J;F=utils.gen_rc_errors(_L,_g,error_message=M);H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=F;return A
		if not _X in Q:
			A=web.Response(status=400)
			if not _X in Q:M=_n+_AH
			A.content_type=J;F=utils.gen_rc_errors(_L,_g,error_message=M);H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=F;return A
		B[_O]['body']=Q;B[_B]={};B[_B][E]={};B[_B][E][G]={};V='/yangcore:preferences/outbound-interactions/'+d
		try:l=await C.dal.handle_get_config_request(V,{})
		except NodeNotFound:B[_B][E][G]['no-callout-configured']=[_C];A=web.Response(status=204);return A
		W=l[d];B[_B][E][G][_G]=W;V=_x+W;I=await C.dal.handle_get_config_request(V,{});assert W==I[_J][0][_G];B[_B][E][G][_p]=I[_J][0][_p];O={};O[_T]=device_id[0];O[_AI]=K.remote;Y=K.transport.get_extra_info(_AG)
		if Y:
			Z=Y.getpeercert(_a)
			if Z:O['identity-certificate']=Z
		if Q:O[_AJ]=Q
		if _Z in I[_J][0]:
			B[_B][E][G][_A4]=_f;a=I[_J][0][_Z][_i];b=I[_J][0][_Z][_f];B[_B][E][G][_AK]={_i:a,_f:b};B[_B][E][G][_d]={}
			if _q in I[_J][0]:c=I[_J][0][_q]
			else:c=_C
			D=_C
			try:D=await C.nvh.plugins[a][_y][b](O,c)
			except Exception as N:B[_B][E][G][_d][_AL]=str(N);A=web.Response(status=500);A.content_type=J;F=utils.gen_rc_errors(_c,_r,error_message='Server encountered an error while trying '+'to process the progress report: '+str(N));H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=F;return A
			if D:
				assert isinstance(D,dict);assert len(D)==1;assert _I in D;assert len(D[_I][_M])==1
				if any(A==D[_I][_M][0][_P]for A in(_Y,'too-big',_AM,_A2,_AN,_AO,_b,_AP,_g)):A=web.Response(status=400)
				elif any(A==D[_I][_M][0][_P]for A in _A3):A=web.Response(status=403)
				elif any(A==D[_I][_M][0][_P]for A in('in-use',_AQ,_AR,_AS,_o)):A=web.Response(status=409)
				elif any(A==D[_I][_M][0][_P]for A in(_AT,_AU,_AV)):A=web.Response(status=500)
				elif any(A==D[_I][_M][0][_P]for A in _r):A=web.Response(status=501)
				else:raise NotImplementedError(_AW+D[_I][_M][0][_P])
				A.content_type=J;F=D;H=C.dm4errors.get_schema_node(_D);A.text=utils.obj_to_encoded_str(F,L,C.dm4errors,H);B[_A][_E]=D;B[_B][E][G][_d][_s]='Returning an RPC-error provided by function '+'(NOTE: RPC-error != exception, hence a normal exit).';return A
			B[_B][E][G][_d][_s]='Function returned no output (normal)'
		elif _A5 in I[_J][0]:
			B[_B][E][G][e]={_t:[]}
			for P in I[_J][0][_A5][_t]:
				R={};R[_G]=P[_G]
				if U in P:
					T='http://'+P[U][X]['remote-address']
					if f in P[U][X]:T+=':'+str(P[U][X][f])
					T+='/relay-notification';R['uri']=T
					try:
						async with aiohttp.ClientSession()as m:A=await m.post(T,data=O)
					except aiohttp.client_exceptions.ClientConnectorError as N:R['connection-error']=str(N)
					else:
						R['http-status-code']=A.status
						if A.status==200:break
				else:assert'https'in P;raise NotImplementedError('https-based webhook is not supported yet.')
				B[_B][E][G][e][_t].append(R)
		else:raise NotImplementedError('unrecognized callout type '+str(I[_J][0]))
		A=web.Response(status=204);return A