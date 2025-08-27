Class Agent.Msg.ShippingStatusReq Extends (Ens.Request, %JSON.Adaptor)
{

Property xRequestId As %String;

Property orderId As %String;

Property orderStatus As %String;

Property trackingNumber As %String;

Storage Default
{
<Data name="ShippingStatusReqDefaultData">
<Subscript>"ShippingStatusReq"</Subscript>
<Value name="1">
<Value>xRequestId</Value>
</Value>
<Value name="2">
<Value>orderId</Value>
</Value>
<Value name="3">
<Value>orderStatus</Value>
</Value>
<Value name="4">
<Value>trackingNumber</Value>
</Value>
</Data>
<DefaultData>ShippingStatusReqDefaultData</DefaultData>
<Type>%Storage.Persistent</Type>
}

}
