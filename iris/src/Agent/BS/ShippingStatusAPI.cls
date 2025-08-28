Class Agent.BS.ShippingStatusAPI Extends (%CSP.REST, Ens.BusinessService)
{

Parameter HandleCorsRequest = 1;

XData UrlMap [ XMLNamespace = "http://www.intersystems.com/urlmap" ]
{
<Routes>
    <Route Method="POST" Url = "/status" Call = "ShippingStatus" />
</Routes>
}

ClassMethod ShippingStatus() As %Status
{
    set ret = $$$OK
    try {
        // request body
        set body = %request.Content

        // instantiate msg from request body payload
        set msg = ##class(Agent.Msg.ShippingStatusReq).%JSONNew()
        $$$ThrowOnError(msg.%JSONImport(body))
        set msg.xRequestId = %request.GetCgiEnv("HTTP_X_REQUEST_ID")

        // instatiate interop business service and send to ingestion process
        $$$ThrowOnError(##class(Ens.Director).CreateBusinessService("Shipping Status API", .service))
        $$$ThrowOnError(service.SendRequestSync("Shipping Info Process", msg, .response))

        set response.info.trace.sessionId = service.%RequestHeader.SessionId
        set response.info.trace.url = "http://localhost:52773/csp/user/EnsPortal.VisualTrace.zen?SESSIONID="_service.%RequestHeader.SessionId
        
        // response
        set %response.Status = "200"
        do response.%JSONExport()

    } catch ex {
        set ret = ex.AsStatus()
        set %response.Status = 500
    }

    quit ret
}

/// Common config
ClassMethod OnPreDispatch(pUrl As %String, pMethod As %String, ByRef pContinue As %Boolean) As %Status
{
    set %response.ContentType = "application/json"
    quit $$$OK
}

}
