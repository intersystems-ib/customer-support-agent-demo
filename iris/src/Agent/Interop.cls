Class Agent.Interop Extends Ens.Production
{

XData ProductionDefinition
{
<Production Name="Agent.Interop" TestingEnabled="true" LogGeneralTraceEvents="false">
  <Description>Agent Interoperability</Description>
  <ActorPoolSize>2</ActorPoolSize>
  <Item Name="Shipping Status API" Category="" ClassName="Agent.BS.ShippingStatusAPI" PoolSize="0" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
  <Item Name="Shipping Info Operation" Category="" ClassName="Agent.BO.ShippingInfo" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
  <Item Name="Shipping Timeline Operation" Category="" ClassName="Agent.BO.ShippingTimeline" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
  <Item Name="Shipping Info Process" Category="" ClassName="Agent.BP.ShippingInfoProcess" PoolSize="1" Enabled="true" Foreground="false" Comment="" LogTraceEvents="false" Schedule="">
  </Item>
</Production>
}

}
