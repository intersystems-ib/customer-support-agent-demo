Class Agent.Msg.ShippingInfoRsp Extends (Ens.Response, %JSON.Adaptor)
{

Property trackingCode As %String;

Property carrier As %String;

Property status As %String;

Property eta As %String;

Property trace As TraceData;

Storage Default
{
<Data name="ShippingInfoRspDefaultData">
<Subscript>"ShippingInfoRsp"</Subscript>
<Value name="1">
<Value>trackingCode</Value>
</Value>
<Value name="2">
<Value>carrier</Value>
</Value>
<Value name="3">
<Value>status</Value>
</Value>
<Value name="4">
<Value>eta</Value>
</Value>
<Value name="5">
<Value>trace</Value>
</Value>
</Data>
<DefaultData>ShippingInfoRspDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
