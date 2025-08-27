Class Agent.Msg.ShippingStatusRsp Extends (Ens.Response, %JSON.Adaptor)
{

Property info As ShippingInfoRsp;

Property timeline As ShippingTimelineRsp;

Storage Default
{
<Data name="ShippingStatusRspDefaultData">
<Subscript>"ShippingStatusRsp"</Subscript>
<Value name="1">
<Value>info</Value>
</Value>
<Value name="2">
<Value>timeline</Value>
</Value>
</Data>
<DefaultData>ShippingStatusRspDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
