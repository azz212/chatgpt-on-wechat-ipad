import json
import xml.etree.ElementTree as ET
from common.log import logger

# XML消息字符串
xml_data_invite = '''
<sysmsg type="sysmsgtemplate">\n\t<sysmsgtemplate>\n\t\t<content_template type="tmpl_type_profile">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name="username" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_gqhxp9ipfxv222]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[🌙 周星星🌙(管理)]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name="names" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[zhaokaihui123]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[大辉辉]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>
'''
xml_data_invite2 ='''
<sysmsg type="sysmsgtemplate">\n\t<sysmsgtemplate>\n\t\t<content_template type="tmpl_type_profile">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name="username" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_gqhxp9ipfxv222]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[🌙 周星星🌙(管理)]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name="names" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_yr9kqgy0sx6s22]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[帅哥]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>
'''
xml_data_invite3 ='''
<sysmsg type="sysmsgtemplate">\n\t<sysmsgtemplate>\n\t\t<content_template type="tmpl_type_profile">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name="username" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_gqhxp9ipfxv222]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[🌙 周星星🌙(管理)]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name="names" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_yr9kqgy0sx6s22]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[帅哥]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>
'''
xml_data_pai ='''
<sysmsg type="pat">\n<pat>\n  <fromusername>wxid_gqhxp9ipfxv222</fromusername>\n  <chatusername>26516713149@chatroom</chatusername>\n  <pattedusername>wxid_6q3ar4xb7m1922</pattedusername>\n  <patsuffix><![CDATA[]]></patsuffix>\n  <patsuffixversion>0</patsuffixversion>\n\n\n\n\n  <template><![CDATA["${wxid_gqhxp9ipfxv222}" 拍了拍我]]></template>\n\n\n\n\n</pat>\n</sysmsg>
'''

xml_data_revokemsg='''
<sysmsg type="revokemsg"><revokemsg><session>26516713149@chatroom</session><msgid>1645246305</msgid><newmsgid>1793967667995376130</newmsgid><replacemsg><![CDATA["🌙 周星星🌙(管理)" 撤回了一条消息]]></replacemsg><announcement_id><![CDATA[]]></announcement_id></revokemsg></sysmsg>
'''
xml_data_revokemsg2='''
<sysmsg type="revokemsg"><revokemsg><session>26516713149@chatroom</session><msgid>1645246345</msgid><newmsgid>573030870260826826</newmsgid><replacemsg><![CDATA["🌙 周星星🌙(管理)" 撤回了一条消息]]></replacemsg><announcement_id><![CDATA[]]></announcement_id></revokemsg></sysmsg>
'''
xml_data_refer = '''
<msg>
	<appmsg appid="" sdkver="0">
		<title>idi</title>
		<des />
		<username />
		<action>view</action>
		<type>57</type>
		<showtype>0</showtype>
		<content />
		<url />
		<lowurl />
		<forwardflag>0</forwardflag>
		<dataurl />
		<lowdataurl />
		<contentattr>0</contentattr>
		<streamvideo>
			<streamvideourl />
			<streamvideototaltime>0</streamvideototaltime>
			<streamvideotitle />
			<streamvideowording />
			<streamvideoweburl />
			<streamvideothumburl />
			<streamvideoaduxinfo />
			<streamvideopublishid />
		</streamvideo>
		<canvasPageItem>
			<canvasPageXml><![CDATA[]]></canvasPageXml>
		</canvasPageItem>
		<refermsg>
			<type>1</type>
			<svrid>5366901243628699568</svrid>
			<fromusr>26516713149@chatroom</fromusr>
			<chatusr>wxid_6q3ar4xb7m1922</chatusr>
			<displayname>帅哥-）</displayname>
			<msgsource>&lt;msgsource&gt;
	&lt;silence&gt;0&lt;/silence&gt;
	&lt;membercount&gt;6&lt;/membercount&gt;
	&lt;signature&gt;V1_S5ypQq/I|v1_S5ypQq/I&lt;/signature&gt;
	&lt;tmp_node&gt;
		&lt;publisher-id&gt;&lt;/publisher-id&gt;
	&lt;/tmp_node&gt;
&lt;/msgsource&gt;
</msgsource>
			<content>
@🌙 周星星🌙(管理)
Here is the image based on your instruction:</content>
			<strid />
			<createtime>1719581858</createtime>
		</refermsg>
		<appattach>
			<totallen>0</totallen>
			<attachid />
			<cdnattachurl />
			<emoticonmd5 />
			<aeskey />
			<fileext />
			<islargefilemsg>0</islargefilemsg>
		</appattach>
		<extinfo />
		<androidsource>0</androidsource>
		<thumburl />
		<mediatagname />
		<messageaction><![CDATA[]]></messageaction>
		<messageext><![CDATA[]]></messageext>
		<emoticongift>
			<packageflag>0</packageflag>
			<packageid />
		</emoticongift>
		<emoticonshared>
			<packageflag>0</packageflag>
			<packageid />
		</emoticonshared>
		<designershared>
			<designeruin>0</designeruin>
			<designername>null</designername>
			<designerrediretcturl><![CDATA[null]]></designerrediretcturl>
		</designershared>
		<emotionpageshared>
			<tid>0</tid>
			<title>null</title>
			<desc>null</desc>
			<iconUrl><![CDATA[null]]></iconUrl>
			<secondUrl>null</secondUrl>
			<pageType>0</pageType>
			<setKey>null</setKey>
		</emotionpageshared>
		<webviewshared>
			<shareUrlOriginal />
			<shareUrlOpen />
			<jsAppId />
			<publisherId />
			<publisherReqId />
		</webviewshared>
		<template_id />
		<md5 />
		<websearch>
			<rec_category>0</rec_category>
			<channelId>0</channelId>
		</websearch>
		<weappinfo>
			<username />
			<appid />
			<appservicetype>0</appservicetype>
			<secflagforsinglepagemode>0</secflagforsinglepagemode>
			<videopageinfo>
				<thumbwidth>0</thumbwidth>
				<thumbheight>0</thumbheight>
				<fromopensdk>0</fromopensdk>
			</videopageinfo>
		</weappinfo>
		<statextstr />
		<musicShareItem>
			<musicDuration>0</musicDuration>
		</musicShareItem>
		<finderLiveProductShare>
			<finderLiveID><![CDATA[]]></finderLiveID>
			<finderUsername><![CDATA[]]></finderUsername>
			<finderObjectID><![CDATA[]]></finderObjectID>
			<finderNonceID><![CDATA[]]></finderNonceID>
			<liveStatus><![CDATA[]]></liveStatus>
			<appId><![CDATA[]]></appId>
			<pagePath><![CDATA[]]></pagePath>
			<productId><![CDATA[]]></productId>
			<coverUrl><![CDATA[]]></coverUrl>
			<productTitle><![CDATA[]]></productTitle>
			<marketPrice><![CDATA[0]]></marketPrice>
			<sellingPrice><![CDATA[0]]></sellingPrice>
			<platformHeadImg><![CDATA[]]></platformHeadImg>
			<platformName><![CDATA[]]></platformName>
			<shopWindowId><![CDATA[]]></shopWindowId>
			<flashSalePrice><![CDATA[0]]></flashSalePrice>
			<flashSaleEndTime><![CDATA[0]]></flashSaleEndTime>
			<ecSource><![CDATA[]]></ecSource>
			<sellingPriceWording><![CDATA[]]></sellingPriceWording>
			<platformIconURL><![CDATA[]]></platformIconURL>
			<firstProductTagURL><![CDATA[]]></firstProductTagURL>
			<firstProductTagAspectRatioString><![CDATA[0.0]]></firstProductTagAspectRatioString>
			<secondProductTagURL><![CDATA[]]></secondProductTagURL>
			<secondProductTagAspectRatioString><![CDATA[0.0]]></secondProductTagAspectRatioString>
			<firstGuaranteeWording><![CDATA[]]></firstGuaranteeWording>
			<secondGuaranteeWording><![CDATA[]]></secondGuaranteeWording>
			<thirdGuaranteeWording><![CDATA[]]></thirdGuaranteeWording>
			<isPriceBeginShow>false</isPriceBeginShow>
			<lastGMsgID><![CDATA[]]></lastGMsgID>
			<promoterKey><![CDATA[]]></promoterKey>
			<discountWording><![CDATA[]]></discountWording>
			<priceSuffixDescription><![CDATA[]]></priceSuffixDescription>
			<showBoxItemStringList />
		</finderLiveProductShare>
		<finderOrder>
			<appID><![CDATA[]]></appID>
			<orderID><![CDATA[]]></orderID>
			<path><![CDATA[]]></path>
			<priceWording><![CDATA[]]></priceWording>
			<stateWording><![CDATA[]]></stateWording>
			<productImageURL><![CDATA[]]></productImageURL>
			<products><![CDATA[]]></products>
			<productsCount><![CDATA[0]]></productsCount>
		</finderOrder>
		<finderShopWindowShare>
			<finderUsername><![CDATA[]]></finderUsername>
			<avatar><![CDATA[]]></avatar>
			<nickname><![CDATA[]]></nickname>
			<commodityInStockCount><![CDATA[]]></commodityInStockCount>
			<appId><![CDATA[]]></appId>
			<path><![CDATA[]]></path>
			<appUsername><![CDATA[]]></appUsername>
			<query><![CDATA[]]></query>
			<liteAppId><![CDATA[]]></liteAppId>
			<liteAppPath><![CDATA[]]></liteAppPath>
			<liteAppQuery><![CDATA[]]></liteAppQuery>
			<platformTagURL><![CDATA[]]></platformTagURL>
			<saleWording><![CDATA[]]></saleWording>
			<lastGMsgID><![CDATA[]]></lastGMsgID>
			<profileTypeWording><![CDATA[]]></profileTypeWording>
			<reputationInfo>
				<hasReputationInfo>0</hasReputationInfo>
				<reputationScore>0</reputationScore>
				<reputationWording />
				<reputationTextColor />
				<reputationLevelWording />
				<reputationBackgroundColor />
			</reputationInfo>
			<productImageURLList />
		</finderShopWindowShare>
		<findernamecard>
			<username />
			<avatar><![CDATA[]]></avatar>
			<nickname />
			<auth_job />
			<auth_icon>0</auth_icon>
			<auth_icon_url />
			<ecSource><![CDATA[]]></ecSource>
			<lastGMsgID><![CDATA[]]></lastGMsgID>
		</findernamecard>
		<finderGuarantee>
			<scene><![CDATA[0]]></scene>
		</finderGuarantee>
		<directshare>0</directshare>
		<gamecenter>
			<namecard>
				<iconUrl />
				<name />
				<desc />
				<tail />
				<jumpUrl />
			</namecard>
		</gamecenter>
		<patMsg>
			<chatUser />
			<records>
				<recordNum>0</recordNum>
			</records>
		</patMsg>
		<secretmsg>
			<issecretmsg>0</issecretmsg>
		</secretmsg>
		<referfromscene>0</referfromscene>
		<gameshare>
			<liteappext>
				<liteappbizdata />
				<liteapppriority>0</liteapppriority>
			</liteappext>
			<gameshareid />
			<sharedata />
			<isvideo>0</isvideo>
			<duration>-1</duration>
			<isexposed>0</isexposed>
			<readtext />
		</gameshare>
		<mpsharetrace>
			<hasfinderelement>0</hasfinderelement>
			<lastgmsgid />
		</mpsharetrace>
		<wxgamecard>
			<framesetname />
			<mbcarddata />
			<minpkgversion />
			<mbcardheight>0</mbcardheight>
			<isoldversion>0</isoldversion>
		</wxgamecard>
	</appmsg>
	<fromusername>wxid_gqhxp9ipfxv222</fromusername>
	<scene>0</scene>
	<appinfo>
		<version>1</version>
		<appname></appname>
	</appinfo>
	<commenturl></commenturl>
</msg>
'''
xml_data_groupchat_content = '''
<msg>
	<appmsg appid="" sdkver="0">
		<title>群聊的聊天记录</title>
		<des>罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]</des>
		<type>19</type>
		<url>https://support.weixin.qq.com/cgi-bin/mmsupport-bin/readtemplate?t=page/favorite_record__w_unsupport</url>
		<appattach>
			<cdnthumbaeskey />
			<aeskey></aeskey>
		</appattach>
		<recorditem><![CDATA[<recordinfo><info>罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]</info><datalist count="5"><dataitem htmlid="fcb6af3209353976c181014856c87c0b" datatype="2" dataid="1470962f778efc34357b5bd83a825ece"><head256md5>1ce2dada03238a5d01f762d7a3de6f32</head256md5><thumbsize>87304</thumbsize><messageuuid>cbe94bb47be2a81964e24f8f58f00d08_</messageuuid><cdnthumburl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042438393439616333372d343437312d343361382d396535322d6266336163616639306562350204059820010201000405004c543e00</cdnthumburl><thumbhead256md5>f42faf5ce6710bd129a3991d971d58ed</thumbhead256md5><sourcetime>2024-06-28 10:28:26</sourcetime><fromnewmsgid>4101820831149983210</fromnewmsgid><thumbfiletype>1</thumbfiletype><datafmt>jpg</datafmt><cdndatakey>5cef0983128f04707fba51f03c5336d8</cdndatakey><datasize>542705</datasize><thumbfullmd5>602e15637e6b65f14a4ee8b0a1ebe8c8</thumbfullmd5><filetype>1</filetype><cdnthumbkey>602e15637e6b65f14a4ee8b0a1ebe8c8</cdnthumbkey><sourcename>罗骁驿-天安数码城T5</sourcename><cdndataurl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042465316636626630612d383530662d343165612d393739372d6561356638386661643165340204059420010201000405004c4c0a00</cdndataurl><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/K05lkCSRMSYicNsgkictm4WfsU4wTYjRpYaA7cSPxBYAJRYuFyAFs1ntJhrQib9cVcia2fwYSkH3L8nENBQj9jrDzhVhzVEnWGEh1agOD12HbXJViayHGiaibmibSnuZu4F9lPqM/132</sourceheadurl><fullmd5>5cef0983128f04707fba51f03c5336d8</fullmd5></dataitem><dataitem htmlid="0d33df07f9e073e11313f2714a67626a" datatype="2" dataid="6a85dbe5bc13b4a234291f2c34e2a84d"><head256md5>00c1fcf15d68171e9762b7e15ecf885d</head256md5><thumbsize>18871</thumbsize><messageuuid>d0f7c29ac2a3e3ead6c69d94c4f1b70d_</messageuuid><cdnthumburl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042462623265373032322d653835332d346630302d393066622d3038663231666561336430660204059820010201000405004c4d3600</cdnthumburl><thumbhead256md5>e78a64c153b7ef987d0e977a9cd7fa46</thumbhead256md5><sourcetime>2024-06-28 10:28:26</sourcetime><fromnewmsgid>3405534072592683929</fromnewmsgid><thumbfiletype>1</thumbfiletype><datafmt>jpg</datafmt><cdndatakey>ae3aba20a11398f9b2eec651333ff2bd</cdndatakey><datasize>1084426</datasize><thumbfullmd5>7d461e22778797cf10c37df7d90e79f5</thumbfullmd5><filetype>1</filetype><cdnthumbkey>7d461e22778797cf10c37df7d90e79f5</cdnthumbkey><sourcename>罗骁驿-天安数码城T5</sourcename><cdndataurl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042430363466326362392d326233352d343031652d623630632d6532626637653630636337330204059420010201000405004c4d9a00</cdndataurl><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/K05lkCSRMSYicNsgkictm4WfsU4wTYjRpYaA7cSPxBYAJRYuFyAFs1ntJhrQib9cVcia2fwYSkH3L8nENBQj9jrDzhVhzVEnWGEh1agOD12HbXJViayHGiaibmibSnuZu4F9lPqM/132</sourceheadurl><fullmd5>ae3aba20a11398f9b2eec651333ff2bd</fullmd5></dataitem><dataitem htmlid="691bec52cfea100106a8daeacfca08d3" datatype="2" dataid="a9a8bedb2f31f5e1bb4b00f9465eb3d6"><head256md5>c144ee963b43a78af82f7556eb4fc23e</head256md5><thumbsize>86218</thumbsize><messageuuid>7fe9e6a9023e82b982f70da771972880_</messageuuid><cdnthumburl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042433343732623862382d633265302d343461662d623938352d6632353932633130393936330204059820010201000405004c575e00</cdnthumburl><thumbhead256md5>e0729876dc902ee6942ecd20a4700580</thumbhead256md5><sourcetime>2024-06-28 10:28:26</sourcetime><fromnewmsgid>2503338207472265190</fromnewmsgid><thumbfiletype>1</thumbfiletype><datafmt>jpg</datafmt><cdndatakey>196adfa8dd7655796b75e9240d36a304</cdndatakey><datasize>625405</datasize><thumbfullmd5>1be3cdc2f1c93424e4998a7bb45b7956</thumbfullmd5><filetype>1</filetype><cdnthumbkey>1be3cdc2f1c93424e4998a7bb45b7956</cdnthumbkey><sourcename>罗骁驿-天安数码城T5</sourcename><cdndataurl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042433353433343531382d383133632d343831342d383935312d6239653937383836303761390204059420010201000405004c54a200</cdndataurl><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/K05lkCSRMSYicNsgkictm4WfsU4wTYjRpYaA7cSPxBYAJRYuFyAFs1ntJhrQib9cVcia2fwYSkH3L8nENBQj9jrDzhVhzVEnWGEh1agOD12HbXJViayHGiaibmibSnuZu4F9lPqM/132</sourceheadurl><fullmd5>196adfa8dd7655796b75e9240d36a304</fullmd5></dataitem><dataitem htmlid="a975b845de2b9cce9c30b73ba2bed5e7" datatype="2" dataid="fa1ee0ef502a50e7a1c8829cf41c283a"><head256md5>ae3a8e381ad602a757ef0ea5161fc01b</head256md5><thumbsize>81306</thumbsize><messageuuid>4bb8e8c10c376c42dfa6a7ec760f4b49_</messageuuid><cdnthumburl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2ba042435666135393139342d393566302d343662632d613831312d6664393666613862633466370204059420010201000405004c54a200</cdnthumburl><thumbhead256md5>fc505cc9f959bd751c9d4f3551fdb4dd</thumbhead256md5><sourcetime>2024-06-28 10:28:26</sourcetime><fromnewmsgid>2624547891192024991</fromnewmsgid><thumbfiletype>1</thumbfiletype><datafmt>jpg</datafmt><cdndatakey>3b87dc24db8067b1dbd01e6e4de53299</cdndatakey><datasize>504793</datasize><thumbfullmd5>2e69f3003877a9cbcae5b819a83f04de</thumbfullmd5><filetype>1</filetype><cdnthumbkey>2e69f3003877a9cbcae5b819a83f04de</cdnthumbkey><sourcename>罗骁驿-天安数码城T5</sourcename><cdndataurl>3057020100044b304902010002049dee1ced02032df7fa02048eebd4760204667ec2bb042436623734613132632d393165612d346132322d393038382d3231313835633563333165310204059420010201000405004c4f2a00</cdndataurl><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/K05lkCSRMSYicNsgkictm4WfsU4wTYjRpYaA7cSPxBYAJRYuFyAFs1ntJhrQib9cVcia2fwYSkH3L8nENBQj9jrDzhVhzVEnWGEh1agOD12HbXJViayHGiaibmibSnuZu4F9lPqM/132</sourceheadurl><fullmd5>3b87dc24db8067b1dbd01e6e4de53299</fullmd5></dataitem><dataitem htmlid="21f49c28b536281e2b2c3ea20a059fb5" datatype="1" dataid="f0766b07a8bb2a130b7cfc9147a22543"><sourcetime>2024-06-28 10:35:02</sourcetime><fromnewmsgid>3524617431912454047</fromnewmsgid><datadesc>成都果然炸裂</datadesc><sourcename>温皇</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/3869cqD6rfADggkVukxWV3Xhn4eg53sVke24zvnyPhLNeHLuzwicWw7gvYYGF6DYBocSBa5rHINJtAjvbmx5NsZT6yVkojyQ0vZIKibn2YATn6WzDicIZXdg0I3xc9pCvsJ/132</sourceheadurl></dataitem></datalist><desc>罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]
罗骁驿-天安数码城T5: [图片]</desc><fromscene>2</fromscene></recordinfo>]]></recorditem>
		<percent>95</percent>
	</appmsg>
	<fromusername>wxid_rfig2xemgdlp21</fromusername>
	<scene>0</scene>
	<appinfo>
		<version>1</version>
		<appname />
	</appinfo>
	<commenturl />
</msg>
'''

def parse_wechat_message(xml_data):
    def get_member_info(member_element):
        if member_element is not None:
            username = member_element.findtext('.//username').strip()
            nickname = member_element.findtext('.//nickname').strip()
            return {
                'username': username,
                'nickname': nickname
            }
        else:
            return None
    # 解析XML
    root = ET.fromstring(xml_data)

    # 获取消息类型
    message_type = root.get('type')
    refermsg = root.find('.//refermsg')
    # 根据消息类型提取信息
    if message_type == 'pat':
        # 拍一拍消息
        from_username = root.find('.//fromusername').text if root.find('.//fromusername') is not None else None
        template_content = root.find('.//template').text if root.find('.//template') is not None else None
        return {
            'message_type': message_type,
            'from_username': from_username,
            'action': template_content
        }
    elif message_type == 'sysmsgtemplate':
        # 系统消息，可能是邀请或撤回
        sub_type = root.find('./subtype').text if root.find('./subtype') is not None else None
        sub_type = root.find('.//sysmsgtemplate/content_template[@type="tmpl_type_profile"]')
        if sub_type :

            # 获取邀请者信息
            inviter_link = root.find('.//link_list/link[@name="username"]')
            inviter = get_member_info(inviter_link.find('.//member') if inviter_link is not None else None)

            # 获取加入群聊的成员信息
            names_link = root.find('.//link_list/link[@name="names"]')
            members = names_link.findall('.//memberlist/member') if names_link is not None else []
            joiners = [get_member_info(member) for member in members if get_member_info(member)]

            return {
                'message_type': message_type,
                'subtype': "invite",
                'inviter_username': inviter,
                'joiners_usernames': joiners
            }
        else:
            return {'message_type': message_type, 'subtype': sub_type, 'info': '未知系统消息类型'}
    elif message_type == 'revokemsg':
        # 消息撤回
        session = root.find('./session').text if root.find('./session') is not None else None
        msgid = root.find('./revokemsg/msgid').text if root.find('./revokemsg/msgid') is not None else None
        newmsgid = root.find('./revokemsg/newmsgid').text if root.find('./revokemsg/newmsgid') is not None else None
        replacemsg = root.find('./revokemsg/replacemsg').text if root.find(
            './revokemsg/replacemsg') is not None else None

        # 返回撤回消息的字典
        return {
            'message_type': 'revokemsg',
            'session': session,
            'original_message_id': msgid,
            'new_message_id': newmsgid,
            'replace_message': replacemsg
        }
    elif message_type == 'NewXmlChatRoomAccessVerifyApplication':
        # 提取关键信息
        # 提取邀请人用户名
        inviter_username = root.find('.//inviterusername').text if root.find(
            './/inviterusername') is not None else "N/A"

        # 从 <text> 标签中提取邀请人的昵称
        text_content = root.find('.//text').text if root.find('.//text') is not None else ""
        start_index = text_content.find('"') + 1
        end_index = text_content.find('"', start_index + 1)
        inviter_nickname = text_content[start_index:end_index] if start_index < end_index else "N/A"

        room_name = root.find('.//RoomName').text if root.find('.//RoomName') is not None else "N/A"
        invitation_reason = root.find('.//invitationreason').text if root.find(
            './/invitationreason') is not None else "N/A"

        joiners = []
        memberlist = root.find('.//memberlist')
        if memberlist is not None:
            for member in memberlist.findall('member'):
                username = member.find('username').text if member.find('username') is not None else "N/A"
                nickname = member.find('nickname').text if member.find('nickname') is not None else "N/A"
                headimgurl = member.find('headimgurl').text if member.find('headimgurl') is not None else "N/A"
                joiners.append({
                    'username': username,
                    'nickname': nickname,
                    'headimgurl': headimgurl
                })

            # 构建JSON结构
        message_info = {
            'message_type': 'NewXmlChatRoomAccessVerifyApplication',
            'subtype': 'invite',
            'inviter_username': inviter_username,
            'inviter_nickname': inviter_nickname,
            'room_name': room_name,
            'invitation_reason': invitation_reason,
            'joiners': joiners
        }

        return json.dumps(message_info, ensure_ascii=False, indent=4)

    elif refermsg is not None:
        # 这是一个引用消息
        logger.info("引用消息存在，提取关键信息：")

        appmsg = root.find('appmsg')
        title = appmsg.find('title').text if appmsg.find('title') is not None else "N/A"

        refer_type = refermsg.find('type').text if refermsg.find('type') is not None else "N/A"
        svrid = refermsg.find('svrid').text if refermsg.find('svrid') is not None else "N/A"
        fromusr = refermsg.find('fromusr').text if refermsg.find('fromusr') is not None else "N/A"
        chatusr = refermsg.find('chatusr').text if refermsg.find('chatusr') is not None else "N/A"
        displayname = refermsg.find('displayname').text if refermsg.find('displayname') is not None else "N/A"
        content = refermsg.find('content').text if refermsg.find('content') is not None else "N/A"
        message_info = {
            'message_type': 'appmsg',
            'title': title,
            'content': content
        }
        # 添加引用消息的信息
        message_info.update({
            'subtype': 'reference',
            'title': title,
            'reference': {
                'type': refer_type,
                'svrid': svrid,
                'fromusr': fromusr,
                'chatusr': chatusr,
                'displayname': displayname,
                'content': content
            }
        })
        # 输出提取的信息
        logger.info(f"消息内容: {title}")
        logger.info(f"引用消息类型: {refer_type}")
        logger.info(f"消息ID: {svrid}")
        logger.info(f"发送人: {fromusr}")
        logger.info(f"聊天群: {chatusr}")
        logger.info(f"显示名: {displayname}")
        logger.info(f"消息内容: {content}")
        return json.dumps(message_info, ensure_ascii=False, indent=4)
    else:
        return {'message_type': message_type, 'info': '未知消息类型'}



# 调用函数并打印结果
parsed_message = parse_wechat_message(xml_data_refer)
print(parsed_message)
#print(f"{parsed_message['inviter_username']['nickname']} 邀请 {parsed_message['joiners_usernames'][0]['nickname'] } 加入了群聊!")