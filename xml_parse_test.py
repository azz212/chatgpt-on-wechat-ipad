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
xml_data_refer_topic = '<msg>\n\t<appmsg appid="" sdkver="0">\n\t\t<title>分析这个</title>\n\t\t<des />\n\t\t<username />\n\t\t<action>view</action>\n\t\t<type>57</type>\n\t\t<showtype>0</showtype>\n\t\t<content />\n\t\t<url />\n\t\t<lowurl />\n\t\t<forwardflag>0</forwardflag>\n\t\t<dataurl />\n\t\t<lowdataurl />\n\t\t<contentattr>0</contentattr>\n\t\t<streamvideo>\n\t\t\t<streamvideourl />\n\t\t\t<streamvideototaltime>0</streamvideototaltime>\n\t\t\t<streamvideotitle />\n\t\t\t<streamvideowording />\n\t\t\t<streamvideoweburl />\n\t\t\t<streamvideothumburl />\n\t\t\t<streamvideoaduxinfo />\n\t\t\t<streamvideopublishid />\n\t\t</streamvideo>\n\t\t<canvasPageItem>\n\t\t\t<canvasPageXml><![CDATA[]]></canvasPageXml>\n\t\t</canvasPageItem>\n\t\t<refermsg>\n\t\t\t<type>49</type>\n\t\t\t<svrid>1221230959438763766</svrid>\n\t\t\t<fromusr>46222487326@chatroom</fromusr>\n\t\t\t<chatusr>wxid_gqhxp9ipfxv222</chatusr>\n\t\t\t<displayname>🌙 周星星🌙</displayname>\n\t\t\t<msgsource>&lt;msgsource&gt;&lt;sec_msg_node&gt;&lt;uuid&gt;9116fff63dc44b91015909d1dfcf7fb6_&lt;/uuid&gt;&lt;/sec_msg_node&gt;&lt;alnode&gt;&lt;fr&gt;4&lt;/fr&gt;&lt;/alnode&gt;&lt;tmp_node&gt;&lt;publisher-id&gt;msg_2165907583058165166|wxid_gqhxp9ipfxv222|49670972421@chatroom&lt;/publisher-id&gt;&lt;/tmp_node&gt;&lt;/msgsource&gt;</msgsource>\n\t\t\t<content>&lt;msg&gt;&lt;appmsg appid="" sdkver="0"&gt;&lt;title&gt;streamlit里的alphalens：单因子分析框架（代码+数据）&lt;/title&gt;&lt;des&gt;原创文章第556篇，专注“AI量化投资、世界运行的规律、个人成长与财富自由&amp;quot;。streamlit里的alphalens：单因子分析框架（代码+数据）&lt;/des&gt;&lt;username&gt;&lt;/username&gt;&lt;action&gt;view&lt;/action&gt;&lt;type&gt;5&lt;/type&gt;&lt;showtype&gt;0&lt;/showtype&gt;&lt;content&gt;&lt;/content&gt;&lt;url&gt;http://mp.weixin.qq.com/s?__biz=MzIwNTU2ODMwNg==&amp;amp;mid=2247491002&amp;amp;idx=1&amp;amp;sn=5b38584a7ea6671d60829f05988e8256&amp;amp;chksm=972fbde7a05834f100631d319fb46e868be14de5f4673a19912fd8cd106cc1aefb1b1e65a4fd&amp;amp;mpshare=1&amp;amp;scene=1&amp;amp;srcid=07071HNqhwZubDawhPtNbSTa&amp;amp;sharer_shareinfo=5b53a184d0c3d96f94b037a0357ca272&amp;amp;sharer_shareinfo_first=5b53a184d0c3d96f94b037a0357ca272#rd&lt;/url&gt;&lt;lowurl&gt;&lt;/lowurl&gt;&lt;forwardflag&gt;0&lt;/forwardflag&gt;&lt;dataurl&gt;&lt;/dataurl&gt;&lt;lowdataurl&gt;&lt;/lowdataurl&gt;&lt;contentattr&gt;0&lt;/contentattr&gt;&lt;streamvideo&gt;&lt;streamvideourl&gt;&lt;/streamvideourl&gt;&lt;streamvideototaltime&gt;0&lt;/streamvideototaltime&gt;&lt;streamvideotitle&gt;&lt;/streamvideotitle&gt;&lt;streamvideowording&gt;&lt;/streamvideowording&gt;&lt;streamvideoweburl&gt;&lt;/streamvideoweburl&gt;&lt;streamvideothumburl&gt;&lt;/streamvideothumburl&gt;&lt;streamvideoaduxinfo&gt;&lt;/streamvideoaduxinfo&gt;&lt;streamvideopublishid&gt;&lt;/streamvideopublishid&gt;&lt;/streamvideo&gt;&lt;canvasPageItem&gt;&lt;canvasPageXml&gt;&lt;![CDATA[]]&gt;&lt;/canvasPageXml&gt;&lt;/canvasPageItem&gt;&lt;appattach&gt;&lt;totallen&gt;0&lt;/totallen&gt;&lt;attachid&gt;&lt;/attachid&gt;&lt;cdnattachurl&gt;&lt;/cdnattachurl&gt;&lt;emoticonmd5&gt;&lt;/emoticonmd5&gt;&lt;aeskey&gt;&lt;/aeskey&gt;&lt;fileext&gt;&lt;/fileext&gt;&lt;islargefilemsg&gt;0&lt;/islargefilemsg&gt;&lt;/appattach&gt;&lt;extinfo&gt;&lt;/extinfo&gt;&lt;androidsource&gt;3&lt;/androidsource&gt;&lt;sourceusername&gt;gh_011e81a0ab37&lt;/sourceusername&gt;&lt;sourcedisplayname&gt;七年实现财富自由&lt;/sourcedisplayname&gt;&lt;commenturl&gt;&lt;/commenturl&gt;&lt;thumburl&gt;&lt;/thumburl&gt;&lt;mediatagname&gt;&lt;/mediatagname&gt;&lt;messageaction&gt;&lt;![CDATA[]]&gt;&lt;/messageaction&gt;&lt;messageext&gt;&lt;![CDATA[]]&gt;&lt;/messageext&gt;&lt;emoticongift&gt;&lt;packageflag&gt;0&lt;/packageflag&gt;&lt;packageid&gt;&lt;/packageid&gt;&lt;/emoticongift&gt;&lt;emoticonshared&gt;&lt;packageflag&gt;0&lt;/packageflag&gt;&lt;packageid&gt;&lt;/packageid&gt;&lt;/emoticonshared&gt;&lt;designershared&gt;&lt;designeruin&gt;0&lt;/designeruin&gt;&lt;designername&gt;null&lt;/designername&gt;&lt;designerrediretcturl&gt;&lt;![CDATA[null]]&gt;&lt;/designerrediretcturl&gt;&lt;/designershared&gt;&lt;emotionpageshared&gt;&lt;tid&gt;0&lt;/tid&gt;&lt;title&gt;null&lt;/title&gt;&lt;desc&gt;null&lt;/desc&gt;&lt;iconUrl&gt;&lt;![CDATA[null]]&gt;&lt;/iconUrl&gt;&lt;secondUrl&gt;null&lt;/secondUrl&gt;&lt;pageType&gt;0&lt;/pageType&gt;&lt;setKey&gt;null&lt;/setKey&gt;&lt;/emotionpageshared&gt;&lt;webviewshared&gt;&lt;shareUrlOriginal&gt;https://mp.weixin.qq.com/s/QYcAhahHYF3hzBV7uz1n4g&lt;/shareUrlOriginal&gt;&lt;shareUrlOpen&gt;https://mp.weixin.qq.com/s?__biz=MzIwNTU2ODMwNg==&amp;amp;mid=2247491002&amp;amp;idx=1&amp;amp;sn=5b38584a7ea6671d60829f05988e8256&amp;amp;ascene=1&amp;amp;devicetype=android-31&amp;amp;version=28002c53&amp;amp;nettype=3gnet&amp;amp;lang=zh_CN&amp;amp;countrycode=CN&amp;amp;exportkey=n_ChQIAhIQ1l01VL%2FppEurSIXnh1WkDhL3AQIE97dBBAEAAAAAAApWM%2BvbolEAAAAOpnltbLcz9gKNyK89dVj0D6xII%2FT9hQSFKrR804R8fFHAyBmMpscQXFq3k4StHUjoKXkV2y5oWqYh3TNQ0KkQrA5nBfA%2FWQgkEU9ksGS7q09L5gEbQtPKeqOmZMtfoAbcBu%2BzLNMzIrfEBUnGN2ndzObAEcnvdUkI3%2BYiBj0E8ZCT5jgjtVOYXr%2F3Ta5Rul4BkV9J%2Fp1ZB%2B6ZAhlggiTKMHJ8Eor2Aw23GDSlvgpayXNFl4HpB5C3y2j5jIZ3%2FHwJ%2F9y6K1MXZldh4lPI%2BRP3RK%2Fh3CSLqclOBHOhzHPOMC4%3D&amp;amp;pass_ticket=35Dl6V0YlPWYy3cdegERUs3HhXqIAHcZouZ7%2Bdr7D8UZDZ75Mr9C2YZOZ0nUznQ5&amp;amp;wx_header=3&lt;/shareUrlOpen&gt;&lt;jsAppId&gt;&lt;/jsAppId&gt;&lt;publisherId&gt;msg_3595701631228532384&lt;/publisherId&gt;&lt;publisherReqId&gt;207592139&lt;/publisherReqId&gt;&lt;/webviewshared&gt;&lt;template_id&gt;&lt;/template_id&gt;&lt;md5&gt;&lt;/md5&gt;&lt;websearch&gt;&lt;rec_category&gt;0&lt;/rec_category&gt;&lt;channelId&gt;0&lt;/channelId&gt;&lt;/websearch&gt;&lt;weappinfo&gt;&lt;username&gt;&lt;/username&gt;&lt;appid&gt;&lt;/appid&gt;&lt;appservicetype&gt;0&lt;/appservicetype&gt;&lt;secflagforsinglepagemode&gt;0&lt;/secflagforsinglepagemode&gt;&lt;videopageinfo&gt;&lt;thumbwidth&gt;0&lt;/thumbwidth&gt;&lt;thumbheight&gt;0&lt;/thumbheight&gt;&lt;fromopensdk&gt;0&lt;/fromopensdk&gt;&lt;/videopageinfo&gt;&lt;/weappinfo&gt;&lt;statextstr&gt;&lt;/statextstr&gt;&lt;mmreadershare&gt;&lt;itemshowtype&gt;0&lt;/itemshowtype&gt;&lt;ispaysubscribe&gt;0&lt;/ispaysubscribe&gt;&lt;/mmreadershare&gt;&lt;musicShareItem&gt;&lt;musicDuration&gt;0&lt;/musicDuration&gt;&lt;/musicShareItem&gt;&lt;finderLiveProductShare&gt;&lt;finderLiveID&gt;&lt;![CDATA[]]&gt;&lt;/finderLiveID&gt;&lt;finderUsername&gt;&lt;![CDATA[]]&gt;&lt;/finderUsername&gt;&lt;finderObjectID&gt;&lt;![CDATA[]]&gt;&lt;/finderObjectID&gt;&lt;finderNonceID&gt;&lt;![CDATA[]]&gt;&lt;/finderNonceID&gt;&lt;liveStatus&gt;&lt;![CDATA[]]&gt;&lt;/liveStatus&gt;&lt;appId&gt;&lt;![CDATA[]]&gt;&lt;/appId&gt;&lt;pagePath&gt;&lt;![CDATA[]]&gt;&lt;/pagePath&gt;&lt;productId&gt;&lt;![CDATA[]]&gt;&lt;/productId&gt;&lt;coverUrl&gt;&lt;![CDATA[]]&gt;&lt;/coverUrl&gt;&lt;productTitle&gt;&lt;![CDATA[]]&gt;&lt;/productTitle&gt;&lt;marketPrice&gt;&lt;![CDATA[0]]&gt;&lt;/marketPrice&gt;&lt;sellingPrice&gt;&lt;![CDATA[0]]&gt;&lt;/sellingPrice&gt;&lt;platformHeadImg&gt;&lt;![CDATA[]]&gt;&lt;/platformHeadImg&gt;&lt;platformName&gt;&lt;![CDATA[]]&gt;&lt;/platformName&gt;&lt;shopWindowId&gt;&lt;![CDATA[]]&gt;&lt;/shopWindowId&gt;&lt;flashSalePrice&gt;&lt;![CDATA[0]]&gt;&lt;/flashSalePrice&gt;&lt;flashSaleEndTime&gt;&lt;![CDATA[0]]&gt;&lt;/flashSaleEndTime&gt;&lt;ecSource&gt;&lt;![CDATA[]]&gt;&lt;/ecSource&gt;&lt;sellingPriceWording&gt;&lt;![CDATA[]]&gt;&lt;/sellingPriceWording&gt;&lt;platformIconURL&gt;&lt;![CDATA[]]&gt;&lt;/platformIconURL&gt;&lt;firstProductTagURL&gt;&lt;![CDATA[]]&gt;&lt;/firstProductTagURL&gt;&lt;firstProductTagAspectRatioString&gt;&lt;![CDATA[0.0]]&gt;&lt;/firstProductTagAspectRatioString&gt;&lt;secondProductTagURL&gt;&lt;![CDATA[]]&gt;&lt;/secondProductTagURL&gt;&lt;secondProductTagAspectRatioString&gt;&lt;![CDATA[0.0]]&gt;&lt;/secondProductTagAspectRatioString&gt;&lt;firstGuaranteeWording&gt;&lt;![CDATA[]]&gt;&lt;/firstGuaranteeWording&gt;&lt;secondGuaranteeWording&gt;&lt;![CDATA[]]&gt;&lt;/secondGuaranteeWording&gt;&lt;thirdGuaranteeWording&gt;&lt;![CDATA[]]&gt;&lt;/thirdGuaranteeWording&gt;&lt;isPriceBeginShow&gt;false&lt;/isPriceBeginShow&gt;&lt;lastGMsgID&gt;&lt;![CDATA[]]&gt;&lt;/lastGMsgID&gt;&lt;promoterKey&gt;&lt;![CDATA[]]&gt;&lt;/promoterKey&gt;&lt;discountWording&gt;&lt;![CDATA[]]&gt;&lt;/discountWording&gt;&lt;priceSuffixDescription&gt;&lt;![CDATA[]]&gt;&lt;/priceSuffixDescription&gt;&lt;showBoxItemStringList&gt;&lt;/showBoxItemStringList&gt;&lt;/finderLiveProductShare&gt;&lt;finderOrder&gt;&lt;appID&gt;&lt;![CDATA[]]&gt;&lt;/appID&gt;&lt;orderID&gt;&lt;![CDATA[]]&gt;&lt;/orderID&gt;&lt;path&gt;&lt;![CDATA[]]&gt;&lt;/path&gt;&lt;priceWording&gt;&lt;![CDATA[]]&gt;&lt;/priceWording&gt;&lt;stateWording&gt;&lt;![CDATA[]]&gt;&lt;/stateWording&gt;&lt;productImageURL&gt;&lt;![CDATA[]]&gt;&lt;/productImageURL&gt;&lt;products&gt;&lt;![CDATA[]]&gt;&lt;/products&gt;&lt;productsCount&gt;&lt;![CDATA[0]]&gt;&lt;/productsCount&gt;&lt;/finderOrder&gt;&lt;finderShopWindowShare&gt;&lt;finderUsername&gt;&lt;![CDATA[]]&gt;&lt;/finderUsername&gt;&lt;avatar&gt;&lt;![CDATA[]]&gt;&lt;/avatar&gt;&lt;nickname&gt;&lt;![CDATA[]]&gt;&lt;/nickname&gt;&lt;commodityInStockCount&gt;&lt;![CDATA[]]&gt;&lt;/commodityInStockCount&gt;&lt;appId&gt;&lt;![CDATA[]]&gt;&lt;/appId&gt;&lt;path&gt;&lt;![CDATA[]]&gt;&lt;/path&gt;&lt;appUsername&gt;&lt;![CDATA[]]&gt;&lt;/appUsername&gt;&lt;query&gt;&lt;![CDATA[]]&gt;&lt;/query&gt;&lt;liteAppId&gt;&lt;![CDATA[]]&gt;&lt;/liteAppId&gt;&lt;liteAppPath&gt;&lt;![CDATA[]]&gt;&lt;/liteAppPath&gt;&lt;liteAppQuery&gt;&lt;![CDATA[]]&gt;&lt;/liteAppQuery&gt;&lt;platformTagURL&gt;&lt;![CDATA[]]&gt;&lt;/platformTagURL&gt;&lt;saleWording&gt;&lt;![CDATA[]]&gt;&lt;/saleWording&gt;&lt;lastGMsgID&gt;&lt;![CDATA[]]&gt;&lt;/lastGMsgID&gt;&lt;profileTypeWording&gt;&lt;![CDATA[]]&gt;&lt;/profileTypeWording&gt;&lt;reputationInfo&gt;&lt;hasReputationInfo&gt;0&lt;/hasReputationInfo&gt;&lt;reputationScore&gt;0&lt;/reputationScore&gt;&lt;reputationWording&gt;&lt;/reputationWording&gt;&lt;reputationTextColor&gt;&lt;/reputationTextColor&gt;&lt;reputationLevelWording&gt;&lt;/reputationLevelWording&gt;&lt;reputationBackgroundColor&gt;&lt;/reputationBackgroundColor&gt;&lt;/reputationInfo&gt;&lt;productImageURLList&gt;&lt;/productImageURLList&gt;&lt;/finderShopWindowShare&gt;&lt;findernamecard&gt;&lt;username&gt;&lt;/username&gt;&lt;avatar&gt;&lt;![CDATA[]]&gt;&lt;/avatar&gt;&lt;nickname&gt;&lt;/nickname&gt;&lt;auth_job&gt;&lt;/auth_job&gt;&lt;auth_icon&gt;0&lt;/auth_icon&gt;&lt;auth_icon_url&gt;&lt;/auth_icon_url&gt;&lt;ecSource&gt;&lt;![CDATA[]]&gt;&lt;/ecSource&gt;&lt;lastGMsgID&gt;&lt;![CDATA[]]&gt;&lt;/lastGMsgID&gt;&lt;/findernamecard&gt;&lt;finderGuarantee&gt;&lt;scene&gt;&lt;![CDATA[0]]&gt;&lt;/scene&gt;&lt;/finderGuarantee&gt;&lt;directshare&gt;0&lt;/directshare&gt;&lt;gamecenter&gt;&lt;namecard&gt;&lt;iconUrl&gt;&lt;/iconUrl&gt;&lt;name&gt;&lt;/name&gt;&lt;desc&gt;&lt;/desc&gt;&lt;tail&gt;&lt;/tail&gt;&lt;jumpUrl&gt;&lt;/jumpUrl&gt;&lt;/namecard&gt;&lt;/gamecenter&gt;&lt;patMsg&gt;&lt;chatUser&gt;&lt;/chatUser&gt;&lt;records&gt;&lt;recordNum&gt;0&lt;/recordNum&gt;&lt;/records&gt;&lt;/patMsg&gt;&lt;secretmsg&gt;&lt;issecretmsg&gt;0&lt;/issecretmsg&gt;&lt;/secretmsg&gt;&lt;referfromscene&gt;0&lt;/referfromscene&gt;&lt;gameshare&gt;&lt;liteappext&gt;&lt;liteappbizdata&gt;&lt;/liteappbizdata&gt;&lt;liteapppriority&gt;0&lt;/liteapppriority&gt;&lt;/liteappext&gt;&lt;gameshareid&gt;&lt;/gameshareid&gt;&lt;sharedata&gt;&lt;/sharedata&gt;&lt;isvideo&gt;0&lt;/isvideo&gt;&lt;duration&gt;-1&lt;/duration&gt;&lt;isexposed&gt;0&lt;/isexposed&gt;&lt;readtext&gt;&lt;/readtext&gt;&lt;/gameshare&gt;&lt;mpsharetrace&gt;&lt;hasfinderelement&gt;0&lt;/hasfinderelement&gt;&lt;lastgmsgid&gt;ChN3eGlkX2dxaHhwOWlwZnh2MjIyEhQ0OTY3MDk3MjQyMUBjaGF0cm9vbSITMjE2NTkwNzU4MzA1ODE2NTE2Ng==&lt;/lastgmsgid&gt;&lt;/mpsharetrace&gt;&lt;wxgamecard&gt;&lt;framesetname&gt;&lt;/framesetname&gt;&lt;mbcarddata&gt;&lt;/mbcarddata&gt;&lt;minpkgversion&gt;&lt;/minpkgversion&gt;&lt;mbcardheight&gt;0&lt;/mbcardheight&gt;&lt;isoldversion&gt;0&lt;/isoldversion&gt;&lt;/wxgamecard&gt;&lt;/appmsg&gt;&lt;/msg&gt;</content>\n\t\t\t<strid />\n\t\t\t<createtime>1720342181</createtime>\n\t\t</refermsg>\n\t\t<appattach>\n\t\t\t<totallen>0</totallen>\n\t\t\t<attachid />\n\t\t\t<cdnattachurl />\n\t\t\t<emoticonmd5 />\n\t\t\t<aeskey />\n\t\t\t<fileext />\n\t\t\t<islargefilemsg>0</islargefilemsg>\n\t\t</appattach>\n\t\t<extinfo />\n\t\t<androidsource>0</androidsource>\n\t\t<thumburl />\n\t\t<mediatagname />\n\t\t<messageaction><![CDATA[]]></messageaction>\n\t\t<messageext><![CDATA[]]></messageext>\n\t\t<emoticongift>\n\t\t\t<packageflag>0</packageflag>\n\t\t\t<packageid />\n\t\t</emoticongift>\n\t\t<emoticonshared>\n\t\t\t<packageflag>0</packageflag>\n\t\t\t<packageid />\n\t\t</emoticonshared>\n\t\t<designershared>\n\t\t\t<designeruin>0</designeruin>\n\t\t\t<designername>null</designername>\n\t\t\t<designerrediretcturl><![CDATA[null]]></designerrediretcturl>\n\t\t</designershared>\n\t\t<emotionpageshared>\n\t\t\t<tid>0</tid>\n\t\t\t<title>null</title>\n\t\t\t<desc>null</desc>\n\t\t\t<iconUrl><![CDATA[null]]></iconUrl>\n\t\t\t<secondUrl>null</secondUrl>\n\t\t\t<pageType>0</pageType>\n\t\t\t<setKey>null</setKey>\n\t\t</emotionpageshared>\n\t\t<webviewshared>\n\t\t\t<shareUrlOriginal />\n\t\t\t<shareUrlOpen />\n\t\t\t<jsAppId />\n\t\t\t<publisherId />\n\t\t\t<publisherReqId />\n\t\t</webviewshared>\n\t\t<template_id />\n\t\t<md5 />\n\t\t<websearch>\n\t\t\t<rec_category>0</rec_category>\n\t\t\t<channelId>0</channelId>\n\t\t</websearch>\n\t\t<weappinfo>\n\t\t\t<username />\n\t\t\t<appid />\n\t\t\t<appservicetype>0</appservicetype>\n\t\t\t<secflagforsinglepagemode>0</secflagforsinglepagemode>\n\t\t\t<videopageinfo>\n\t\t\t\t<thumbwidth>0</thumbwidth>\n\t\t\t\t<thumbheight>0</thumbheight>\n\t\t\t\t<fromopensdk>0</fromopensdk>\n\t\t\t</videopageinfo>\n\t\t</weappinfo>\n\t\t<statextstr />\n\t\t<musicShareItem>\n\t\t\t<musicDuration>0</musicDuration>\n\t\t</musicShareItem>\n\t\t<finderLiveProductShare>\n\t\t\t<finderLiveID><![CDATA[]]></finderLiveID>\n\t\t\t<finderUsername><![CDATA[]]></finderUsername>\n\t\t\t<finderObjectID><![CDATA[]]></finderObjectID>\n\t\t\t<finderNonceID><![CDATA[]]></finderNonceID>\n\t\t\t<liveStatus><![CDATA[]]></liveStatus>\n\t\t\t<appId><![CDATA[]]></appId>\n\t\t\t<pagePath><![CDATA[]]></pagePath>\n\t\t\t<productId><![CDATA[]]></productId>\n\t\t\t<coverUrl><![CDATA[]]></coverUrl>\n\t\t\t<productTitle><![CDATA[]]></productTitle>\n\t\t\t<marketPrice><![CDATA[0]]></marketPrice>\n\t\t\t<sellingPrice><![CDATA[0]]></sellingPrice>\n\t\t\t<platformHeadImg><![CDATA[]]></platformHeadImg>\n\t\t\t<platformName><![CDATA[]]></platformName>\n\t\t\t<shopWindowId><![CDATA[]]></shopWindowId>\n\t\t\t<flashSalePrice><![CDATA[0]]></flashSalePrice>\n\t\t\t<flashSaleEndTime><![CDATA[0]]></flashSaleEndTime>\n\t\t\t<ecSource><![CDATA[]]></ecSource>\n\t\t\t<sellingPriceWording><![CDATA[]]></sellingPriceWording>\n\t\t\t<platformIconURL><![CDATA[]]></platformIconURL>\n\t\t\t<firstProductTagURL><![CDATA[]]></firstProductTagURL>\n\t\t\t<firstProductTagAspectRatioString><![CDATA[0.0]]></firstProductTagAspectRatioString>\n\t\t\t<secondProductTagURL><![CDATA[]]></secondProductTagURL>\n\t\t\t<secondProductTagAspectRatioString><![CDATA[0.0]]></secondProductTagAspectRatioString>\n\t\t\t<firstGuaranteeWording><![CDATA[]]></firstGuaranteeWording>\n\t\t\t<secondGuaranteeWording><![CDATA[]]></secondGuaranteeWording>\n\t\t\t<thirdGuaranteeWording><![CDATA[]]></thirdGuaranteeWording>\n\t\t\t<isPriceBeginShow>false</isPriceBeginShow>\n\t\t\t<lastGMsgID><![CDATA[]]></lastGMsgID>\n\t\t\t<promoterKey><![CDATA[]]></promoterKey>\n\t\t\t<discountWording><![CDATA[]]></discountWording>\n\t\t\t<priceSuffixDescription><![CDATA[]]></priceSuffixDescription>\n\t\t\t<showBoxItemStringList />\n\t\t</finderLiveProductShare>\n\t\t<finderOrder>\n\t\t\t<appID><![CDATA[]]></appID>\n\t\t\t<orderID><![CDATA[]]></orderID>\n\t\t\t<path><![CDATA[]]></path>\n\t\t\t<priceWording><![CDATA[]]></priceWording>\n\t\t\t<stateWording><![CDATA[]]></stateWording>\n\t\t\t<productImageURL><![CDATA[]]></productImageURL>\n\t\t\t<products><![CDATA[]]></products>\n\t\t\t<productsCount><![CDATA[0]]></productsCount>\n\t\t</finderOrder>\n\t\t<finderShopWindowShare>\n\t\t\t<finderUsername><![CDATA[]]></finderUsername>\n\t\t\t<avatar><![CDATA[]]></avatar>\n\t\t\t<nickname><![CDATA[]]></nickname>\n\t\t\t<commodityInStockCount><![CDATA[]]></commodityInStockCount>\n\t\t\t<appId><![CDATA[]]></appId>\n\t\t\t<path><![CDATA[]]></path>\n\t\t\t<appUsername><![CDATA[]]></appUsername>\n\t\t\t<query><![CDATA[]]></query>\n\t\t\t<liteAppId><![CDATA[]]></liteAppId>\n\t\t\t<liteAppPath><![CDATA[]]></liteAppPath>\n\t\t\t<liteAppQuery><![CDATA[]]></liteAppQuery>\n\t\t\t<platformTagURL><![CDATA[]]></platformTagURL>\n\t\t\t<saleWording><![CDATA[]]></saleWording>\n\t\t\t<lastGMsgID><![CDATA[]]></lastGMsgID>\n\t\t\t<profileTypeWording><![CDATA[]]></profileTypeWording>\n\t\t\t<reputationInfo>\n\t\t\t\t<hasReputationInfo>0</hasReputationInfo>\n\t\t\t\t<reputationScore>0</reputationScore>\n\t\t\t\t<reputationWording />\n\t\t\t\t<reputationTextColor />\n\t\t\t\t<reputationLevelWording />\n\t\t\t\t<reputationBackgroundColor />\n\t\t\t</reputationInfo>\n\t\t\t<productImageURLList />\n\t\t</finderShopWindowShare>\n\t\t<findernamecard>\n\t\t\t<username />\n\t\t\t<avatar><![CDATA[]]></avatar>\n\t\t\t<nickname />\n\t\t\t<auth_job />\n\t\t\t<auth_icon>0</auth_icon>\n\t\t\t<auth_icon_url />\n\t\t\t<ecSource><![CDATA[]]></ecSource>\n\t\t\t<lastGMsgID><![CDATA[]]></lastGMsgID>\n\t\t</findernamecard>\n\t\t<finderGuarantee>\n\t\t\t<scene><![CDATA[0]]></scene>\n\t\t</finderGuarantee>\n\t\t<directshare>0</directshare>\n\t\t<gamecenter>\n\t\t\t<namecard>\n\t\t\t\t<iconUrl />\n\t\t\t\t<name />\n\t\t\t\t<desc />\n\t\t\t\t<tail />\n\t\t\t\t<jumpUrl />\n\t\t\t</namecard>\n\t\t</gamecenter>\n\t\t<patMsg>\n\t\t\t<chatUser />\n\t\t\t<records>\n\t\t\t\t<recordNum>0</recordNum>\n\t\t\t</records>\n\t\t</patMsg>\n\t\t<secretmsg>\n\t\t\t<issecretmsg>0</issecretmsg>\n\t\t</secretmsg>\n\t\t<referfromscene>0</referfromscene>\n\t\t<gameshare>\n\t\t\t<liteappext>\n\t\t\t\t<liteappbizdata />\n\t\t\t\t<liteapppriority>0</liteapppriority>\n\t\t\t</liteappext>\n\t\t\t<gameshareid />\n\t\t\t<sharedata />\n\t\t\t<isvideo>0</isvideo>\n\t\t\t<duration>-1</duration>\n\t\t\t<isexposed>0</isexposed>\n\t\t\t<readtext />\n\t\t</gameshare>\n\t\t<mpsharetrace>\n\t\t\t<hasfinderelement>0</hasfinderelement>\n\t\t\t<lastgmsgid />\n\t\t</mpsharetrace>\n\t\t<wxgamecard>\n\t\t\t<framesetname />\n\t\t\t<mbcarddata />\n\t\t\t<minpkgversion />\n\t\t\t<mbcardheight>0</mbcardheight>\n\t\t\t<isoldversion>0</isoldversion>\n\t\t</wxgamecard>\n\t</appmsg>\n\t<fromusername>wxid_gqhxp9ipfxv222</fromusername>\n\t<scene>0</scene>\n\t<appinfo>\n\t\t<version>1</version>\n\t\t<appname></appname>\n\t</appinfo>\n\t<commenturl></commenturl>\n</msg>'
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
xml_data_groupchat_content2 = '''
<msg>
	<appmsg>
		<title>群聊的聊天记录</title>
		<des>帅哥-）: @🌙 周星星🌙(管理)
你好！有什么可以帮助你的吗？
大辉辉: &gt;KFC
帅哥-）: @大辉辉
吵什么吵，就这么一点事。今天我们大家之所以欢聚在这里，是为我们从小到大的好朋友肯德基 ，庆祝他的星期四
大辉辉: &gt;KFC
大辉辉: &gt;看图猜成语...</des>
		<action>view</action>
		<type>19</type>
		<url>https://support.weixin.qq.com/cgi-bin/mmsupport-bin/readtemplate?t=page/favorite_record__w_unsupport&amp;from=singlemessage&amp;isappinstalled=0</url>
		<recorditem><![CDATA[<recordinfo><title>群聊的聊天记录</title><desc>帅哥-）:&#x20;@🌙&#x20;周星星🌙(管理)&#x0A;你好！有什么可以帮助你的吗？&#x0A;大辉辉:&#x20;&gt;KFC&#x0A;帅哥-）:&#x20;@大辉辉&#x0A;吵什么吵，就这么一点事。今天我们大家之所以欢聚在这里，是为我们从小到大的好朋友肯德基&#x20;，庆祝他的星期四&#x0A;大辉辉:&#x20;&gt;KFC&#x0A;大辉辉:&#x20;&gt;看图猜成语...</desc><datalist count="5"><dataitem datatype="1" datasourceid="6979062621926085042"><datadesc>@🌙&#x20;周星星🌙(管理)&#x0A;你好！有什么可以帮助你的吗？</datadesc><sourcename>帅哥-）</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/FwBkrzxbpk2kE0VkuoWoBs4nau1CIEMibvyIMeOWdg3lXoh6OI4IcEgtAfqZBpuIuVia0Pr9nn8dokdTpL6eL2pl88mryNG3kqmQUa9ftSEEI/96</sourceheadurl><sourcetime>2024-06-28&#x20;23:35:44</sourcetime><srcMsgCreateTime>1719588944</srcMsgCreateTime><fromnewmsgid>6979062621926085042</fromnewmsgid><dataitemsource><hashusername>f73f7d69cf58afce3512f24aa9c2b107c0e7ed01b9b598a469944caaf84517e6</hashusername></dataitemsource></dataitem><dataitem datatype="1" datasourceid="2338851685868581048"><datadesc>&gt;KFC</datadesc><sourcename>大辉辉</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/3hWJ41nBHJwWj1GzKg2vwUIo6ffibBx4tra1rN05VSRq0sWsTbNOEiauQsEuKOwWR0cqAItr4RqU7gGibjPr6n26mpNbDnMLcMicI1Zcbic5uibA0/132</sourceheadurl><sourcetime>2024-06-28&#x20;23:35:54</sourcetime><srcMsgCreateTime>1719588954</srcMsgCreateTime><fromnewmsgid>2338851685868581048</fromnewmsgid><dataitemsource><hashusername>e61739c6bed993dc6aa8b03e1ea9ecb4e188358a76d124dc7182b38a313d9f8f</hashusername></dataitemsource></dataitem><dataitem datatype="1" datasourceid="5934468034218630684"><datadesc>@大辉辉&#x0A;吵什么吵，就这么一点事。今天我们大家之所以欢聚在这里，是为我们从小到大的好朋友肯德基&#x20;，庆祝他的星期四</datadesc><sourcename>帅哥-）</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/FwBkrzxbpk2kE0VkuoWoBs4nau1CIEMibvyIMeOWdg3lXoh6OI4IcEgtAfqZBpuIuVia0Pr9nn8dokdTpL6eL2pl88mryNG3kqmQUa9ftSEEI/96</sourceheadurl><sourcetime>2024-06-28&#x20;23:35:57</sourcetime><srcMsgCreateTime>1719588957</srcMsgCreateTime><fromnewmsgid>5934468034218630684</fromnewmsgid><dataitemsource><hashusername>f73f7d69cf58afce3512f24aa9c2b107c0e7ed01b9b598a469944caaf84517e6</hashusername></dataitemsource></dataitem><dataitem datatype="1" datasourceid="8172407547949143523"><datadesc>&gt;KFC</datadesc><sourcename>大辉辉</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/3hWJ41nBHJwWj1GzKg2vwUIo6ffibBx4tra1rN05VSRq0sWsTbNOEiauQsEuKOwWR0cqAItr4RqU7gGibjPr6n26mpNbDnMLcMicI1Zcbic5uibA0/132</sourceheadurl><sourcetime>2024-06-28&#x20;23:40:12</sourcetime><srcMsgCreateTime>1719589212</srcMsgCreateTime><fromnewmsgid>8172407547949143523</fromnewmsgid><dataitemsource><hashusername>e61739c6bed993dc6aa8b03e1ea9ecb4e188358a76d124dc7182b38a313d9f8f</hashusername></dataitemsource></dataitem><dataitem datatype="1" datasourceid="2940445862725204673"><datadesc>&gt;看图猜成语</datadesc><sourcename>大辉辉</sourcename><sourceheadurl>https://wx.qlogo.cn/mmhead/ver_1/3hWJ41nBHJwWj1GzKg2vwUIo6ffibBx4tra1rN05VSRq0sWsTbNOEiauQsEuKOwWR0cqAItr4RqU7gGibjPr6n26mpNbDnMLcMicI1Zcbic5uibA0/132</sourceheadurl><sourcetime>2024-06-28&#x20;23:40:39</sourcetime><srcMsgCreateTime>1719589239</srcMsgCreateTime><fromnewmsgid>2940445862725204673</fromnewmsgid><dataitemsource><hashusername>e61739c6bed993dc6aa8b03e1ea9ecb4e188358a76d124dc7182b38a313d9f8f</hashusername></dataitemsource></dataitem></datalist><favcreatetime>1719591294759</favcreatetime></recordinfo>]]></recorditem>
		<appattach />
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
        try:
            root2 =  ET.fromstring(content)
            url = root2.find('.//url').text if root2.find('.//url') is not None else "N/A"
        except:
            url =""
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
                'content': content,
                'url':url
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
        logger.info(f"URl: {url}")


        return json.dumps(message_info, ensure_ascii=False, indent=4)
    else:
        return {'message_type': message_type, 'info': '未知消息类型'}



# 调用函数并打印结果
parsed_message = parse_wechat_message(xml_data_refer)
print(parsed_message)
#print(f"{parsed_message['inviter_username']['nickname']} 邀请 {parsed_message['joiners_usernames'][0]['nickname'] } 加入了群聊!")
