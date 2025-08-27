Class Agent.Msg.ShippingTimelineRsp Extends (Ens.Response, %JSON.Adaptor)
{

Property events As list Of TimelineData;

Storage Default
{
<Data name="ShippingTimelineRspDefaultData">
<Subscript>"ShippingTimelineRsp"</Subscript>
<Value name="1">
<Value>events</Value>
</Value>
</Data>
<DefaultData>ShippingTimelineRspDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
