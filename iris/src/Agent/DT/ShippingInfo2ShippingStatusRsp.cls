Class Agent.DT.ShippingInfo2ShippingStatusRsp Extends Ens.DataTransformDTL [ DependsOn = (Agent.Msg.ShippingInfoRsp, Agent.Msg.ShippingStatusRsp) ]
{

Parameter GENERATEEMPTYSEGMENTS = 0;

Parameter IGNOREMISSINGSOURCE = 1;

Parameter REPORTERRORS = 1;

Parameter TREATEMPTYREPEATINGFIELDASNULL = 0;

XData DTL [ XMLNamespace = "http://www.intersystems.com/dtl" ]
{
<transform sourceClass='Agent.Msg.ShippingInfoRsp' targetClass='Agent.Msg.ShippingStatusRsp' create='new' language='objectscript' >
<assign value='source.trackingCode' property='target.info.trackingCode' action='set' />
<assign value='source.carrier' property='target.info.carrier' action='set' />
<assign value='source.status' property='target.info.status' action='set' />
<assign value='source.eta' property='target.info.eta' action='set' />
</transform>
}

}
