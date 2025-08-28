/// 
/// Simulates Shiipping Information retrieval
/// - In a real scenario, this would call an external API (e.g. FedEx, UPS, etc.)
Class Agent.BO.ShippingInfo Extends Ens.BusinessOperation
{

Method GeneralInfo(pRequest As Agent.Msg.ShippingStatusReq, pResponse As Agent.Msg.ShippingInfoRsp) As %Status
{
    set ret = $$$OK

    try {
        set pResponse = ##class(Agent.Msg.ShippingInfoRsp).%New()
        set pResponse.trackingCode = pRequest.trackingNumber
        set pResponse.carrier = $extract(pRequest.trackingNumber, 1, 3)
        
        if pRequest.orderStatus = "Delivered" {
            set pResponse.status = "Delivered"
        } else {
            set pResponse.status = "In Transit"
            set pResponse.eta = $zdate($horolog+1+$random(7), 3)
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
		<Method>GeneralInfo</Method>
	</MapItem>
</MapItems>
}

}
