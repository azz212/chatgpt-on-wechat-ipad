import xml.etree.ElementTree as ET

# 你的XML数据
xml_data = '''<?xml version="1.0"?>
<msg>
	<appmsg appid="" sdkver="0">
		<title>好用的语音转文字工具，离线免费使用</title>
		<des>好用的语音转文字工具，离线免费使用</des>
		<username />
		<action>view</action>
		<type>5</type>
		<showtype>0</showtype>
		<content />
		<url>http://mp.weixin.qq.com/s?__biz=MzU2MzYwNTMwNQ==&amp;mid=2247488466&amp;idx=1&amp;sn=e458d29c37c29d9a5a66e31c36ffdb0f&amp;chksm=fc56e984cb21609273c4c348cee93aa05920e29de7ddade34c0ae11598b89517c90d88190584&amp;mpshare=1&amp;scene=1&amp;srcid=0618cxlEejcVsvsxD2pTDOwB&amp;sharer_shareinfo=59e0b2ec988f958272176a2a77569688&amp;sharer_shareinfo_first=59e0b2ec988f958272176a2a77569688#rd</url>
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
		<appattach>
			<attachid />
			<cdnthumburl>3052020100044b3049020100020461cefcb302032f54060204ecee903a02046671833c042439646264333866612d323363312d343862312d613832332d3731316532646265306237630204051808030201000400</cdnthumburl>
			<cdnthumbmd5>03c2e3bad425c6e2a6c006191aba8aa8</cdnthumbmd5>
			<cdnthumblength>14790</cdnthumblength>
			<cdnthumbheight>120</cdnthumbheight>
			<cdnthumbwidth>120</cdnthumbwidth>
			<cdnthumbaeskey>42cce91605d51c8d6d5e45ccb675781d</cdnthumbaeskey>
			<aeskey>42cce91605d51c8d6d5e45ccb675781d</aeskey>
			<encryver>1</encryver>
			<fileext />
			<islargefilemsg>0</islargefilemsg>
		</appattach>
		<extinfo />
		<androidsource>3</androidsource>
		<sourceusername>gh_c1016d1b8d90</sourceusername>
		<sourcedisplayname>GitHub AI开源</sourcedisplayname>
		<commenturl />
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
			<shareUrlOriginal>http://mp.weixin.qq.com/s?chksm=fc56e984cb21609273c4c348cee93aa05920e29de7ddade34c0ae11598b89517c90d88190584&amp;exptype=unsubscribed_card_recommend_article_u2i_mainprocess_coarse_sort_tlfeeds&amp;ranksessionid=1718713052&amp;mid=2247488466&amp;sn=e458d29c37c29d9a5a66e31c36ffdb0f&amp;idx=1&amp;__biz=MzU2MzYwNTMwNQ%3D%3D&amp;scene=169&amp;subscene=200&amp;sessionid=1718713052&amp;flutter_pos=201&amp;clicktime=1718713329&amp;enterid=1718713329&amp;finder_biz_enter_id=5&amp;ascene=56&amp;fasttmpl_type=0&amp;fasttmpl_fullversion=7256626-zh_CN-zip&amp;fasttmpl_flag=0&amp;realreporttime=1718713329606#rd</shareUrlOriginal>
			<shareUrlOpen>https://mp.weixin.qq.com/s?chksm=fc56e984cb21609273c4c348cee93aa05920e29de7ddade34c0ae11598b89517c90d88190584&amp;exptype=unsubscribed_card_recommend_article_u2i_mainprocess_coarse_sort_tlfeeds&amp;ranksessionid=1718713052&amp;mid=2247488466&amp;sn=e458d29c37c29d9a5a66e31c36ffdb0f&amp;idx=1&amp;__biz=MzU2MzYwNTMwNQ%3D%3D&amp;scene=169&amp;subscene=200&amp;sessionid=1718713052&amp;flutter_pos=201&amp;clicktime=1718713329&amp;enterid=1718713329&amp;finder_biz_enter_id=5&amp;ascene=56&amp;fasttmpl_type=0&amp;fasttmpl_fullversion=7256626-zh_CN-zip&amp;fasttmpl_flag=0&amp;realreporttime=1718713329606&amp;devicetype=android-31&amp;version=28002c53&amp;nettype=WIFI&amp;lang=zh_CN&amp;session_us=gh_c1016d1b8d90&amp;countrycode=CN&amp;exportkey=n_ChQIAhIQWBWz4EZ1he6jqrkMwgAoWBLxAQIE97dBBAEAAAAAAAqeJoJ1oLcAAAAOpnltbLcz9gKNyK89dVj0RQVB9ZtRRCd0Y32akNKd94zgPvCzXRU2JLz4DC%2FcciKZgANjn4SwCgNnoh82dyR3rH1x6FYCYk2zFEYrdqHTb3gIfaq4uETZ3H3RzxoOCtx3vXq3E4gS%2BIF0inf56w6xS3Hcr795niIP%2BwTNWMDCA32ExcKqHXT8AyyaIdOeuXjO6XwHaaIagIhr%2FDoPsDbEcScRTsBwR3fUE1pesZE2YHzRPKHPBiu05FiZ9pByFeO7rHZfvHcXRMpuUcix4dKPPHXDPBCOs8aMjMo%3D&amp;pass_ticket=Baws%2BKFyAAc4vfVin7FnkkQ5hxmei2UxCcv%2B0dXjTqSZEyQ94k30K0yd8f5nF6TJ&amp;wx_header=3</shareUrlOpen>
			<jsAppId />
			<publisherId>msg_0</publisherId>
			<publisherReqId>726369597</publisherReqId>
		</webviewshared>
		<template_id />
		<md5>03c2e3bad425c6e2a6c006191aba8aa8</md5>
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
				<thumbwidth>120</thumbwidth>
				<thumbheight>120</thumbheight>
				<fromopensdk>0</fromopensdk>
			</videopageinfo>
		</weappinfo>
		<statextstr />
		<mmreadershare>
			<itemshowtype>0</itemshowtype>
			<ispaysubscribe>0</ispaysubscribe>
		</mmreadershare>
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
			<lastgmsgid>ChN3eGlkX2dxaHhwOWlwZnh2MjIyEhQzODk3Mjg3MzI2MUBjaGF0cm9vbSITNTc1NTU1NzYzMzc2OTE0MDM5MQ==</lastgmsgid>
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
</msg>'''

# 解析XML数据
root = ET.fromstring(xml_data)

# 获取<title>标签的文本内容
title = root.find('.//title').text

# 获取<url>标签的文本内容
url = root.find('.//url').text

print("Title:", title)
print("URL:", url)