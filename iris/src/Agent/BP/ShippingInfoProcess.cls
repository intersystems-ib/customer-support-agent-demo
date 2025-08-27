/// 
Class Agent.BP.ShippingInfoProcess Extends Ens.BusinessProcessBPL
{

Storage Default
{
<Type>%Storage.Persistent</Type>
}

/// BPL Definition
XData BPL [ XMLNamespace = "http://www.intersystems.com/bpl" ]
{
<process language='objectscript' request='Agent.Msg.ShippingStatusReq' response='Agent.Msg.ShippingStatusRsp' height='2000' width='2000' >
<context>
<property name='shippingInfoRsp' type='Agent.Msg.ShippingInfoRsp' instantiate='0' deletewithcontext='0' />
<property name='shippingTimelineRsp' type='Agent.Msg.ShippingTimelineRsp' instantiate='0' deletewithcontext='0' />
</context>
<sequence xend='200' yend='900' >
<call name='Shipping Info Op' target='Shipping Info Operation' async='0' timeout='5' xpos='200' ypos='250' >
<annotation><![CDATA[Get General Shipping Info]]></annotation>
<request type='Agent.Msg.ShippingStatusReq' >
<assign property="callrequest" value="request" action="set" />
</request>
<response type='Agent.Msg.ShippingInfoRsp' >
<assign property="context.shippingInfoRsp" value="callresponse" action="set" />
</response>
</call>
<if name='Response?' condition='context.shippingInfoRsp&apos;=""' xpos='200' ypos='350' xend='200' yend='800' >
<true>
<call name='Shipping Timeline Op' target='Shipping Timeline Operation' async='0' timeout='5' xpos='335' ypos='500' >
<annotation><![CDATA[Get Shipping Timeline Info]]></annotation>
<request type='Agent.Msg.ShippingStatusReq' >
<assign property="callrequest" value="request" action="set" />
</request>
<response type='Agent.Msg.ShippingTimelineRsp' >
<assign property="context.shippingTimelineRsp" value="callresponse" action="set" />
</response>
</call>
<transform name='Add Info To Response' class='Agent.DT.ShippingInfo2ShippingStatusRsp' source='context.shippingInfoRsp' target='response' xpos='335' ypos='600' />
<transform name='Add Timeline to Response' class='Agent.DT.ShippingTimeline2ShippingStatusRsp' source='context.shippingTimelineRsp' target='response' xpos='335' ypos='700' />
</true>
</if>
</sequence>
</process>
}

}
