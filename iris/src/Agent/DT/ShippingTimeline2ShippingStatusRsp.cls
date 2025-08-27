Class Agent.DT.ShippingTimeline2ShippingStatusRsp Extends Ens.DataTransformDTL [ DependsOn = (Agent.Msg.ShippingTimelineRsp, Agent.Msg.ShippingStatusRsp) ]
{

Parameter GENERATEEMPTYSEGMENTS = 0;

Parameter IGNOREMISSINGSOURCE = 1;

Parameter REPORTERRORS = 1;

Parameter TREATEMPTYREPEATINGFIELDASNULL = 0;

XData DTL [ XMLNamespace = "http://www.intersystems.com/dtl" ]
{
<transform sourceClass='Agent.Msg.ShippingTimelineRsp' targetClass='Agent.Msg.ShippingStatusRsp' create='existing' language='objectscript' >
<foreach property='source.events()' key='k1' >
<assign value='source.events.(k1).timestamp' property='target.timeline.events.(k1).timestamp' action='set' />
<assign value='source.events.(k1).description' property='target.timeline.events.(k1).description' action='set' />
<assign value='source.events.(k1).location' property='target.timeline.events.(k1).location' action='set' />
</foreach>
</transform>
}

}
