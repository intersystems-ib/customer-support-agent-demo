Class Agent.Msg.TimelineData Extends (%SerialObject, %XML.Adaptor, %JSON.Adaptor)
{

Property timestamp As %TimeStamp;

Property description As %String;

Property location As %String;

Storage Default
{
<Data name="TimelineDataState">
<Value name="1">
<Value>timestamp</Value>
</Value>
<Value name="2">
<Value>description</Value>
</Value>
<Value name="3">
<Value>location</Value>
</Value>
</Data>
<State>TimelineDataState</State>
<StreamLocation>^Agent.Msg.TimelineDataS</StreamLocation>
<Type>%Storage.Serial</Type>
}

}
