Class Agent.BO.ShippingTimeline Extends Ens.BusinessOperation
{

Method Timeline(pRequest As Agent.Msg.ShippingStatusReq, pResponse As Agent.Msg.ShippingTimelineRsp) As %Status
{
    set ret = $$$OK

    try {
        set locations = $lb("Madrid, ES", "Paris, FR", "Berlin, DE", "Rome, IT", "New York, US")

        set pResponse = ##class(Agent.Msg.ShippingTimelineRsp).%New()

        set event = ##class(Agent.Msg.TimelineData).%New()
        set event.timestamp = $zdatetime($horolog - (7+$random(3)), 3)
        set event.location = $listget(locations, 1+$random($listlength(locations)))
        set event.description = "Package in transit"
        do pResponse.events.Insert(event)

        if pRequest.orderStatus = "Delivered" {
            set event = ##class(Agent.Msg.TimelineData).%New()
            set event.timestamp = $zdatetime($horolog - (1+$random(3)), 3)
            set event.location = $listget(locations, 1+$random($listlength(locations)))
            set event.description = "Package delivered to customer"
            do pResponse.events.Insert(event)   
        }

    } catch ex {
        set ret = ex.AsStatus()
    }

    quit ret
}

XData MessageMap
{
<MapItems>
	<MapItem MessageType="Agent.Msg.ShippingStatusReq"> 
		<Method>Timeline</Method>
	</MapItem>
</MapItems>
}

}
