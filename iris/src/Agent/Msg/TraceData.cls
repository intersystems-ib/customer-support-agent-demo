Class Agent.Msg.TraceData Extends (%SerialObject, %XML.Adaptor, %JSON.Adaptor)
{

Property sessionId As %String;

Property url As %String;

Storage Default
{
<Data name="TraceDataState">
<Value name="1">
<Value>sessionId</Value>
</Value>
<Value name="2">
<Value>url</Value>
</Value>
</Data>
<State>TraceDataState</State>
<StreamLocation>^Agent.Msg.TraceDataS</StreamLocation>
<Type>%Storage.Serial</Type>
}

}
