/// IRIS Embedding Class for Ollama API
/// This class implements the %Embedding.Interface to interact with the Ollama embedding API.
Class Embedding.Ollama Extends %Embedding.Interface
{

/// Validates %Embedding.Config's Configuration property
ClassMethod IsValidConfig(config As %DynamicObject, ByRef errorMsg As %String) As %Boolean
{
    if config.%Get("modelName") = "" {
        set errorMsg = $$$Text("'modelName' not set", "%SQL.VECTOR")
        return 0
    }
    if config.%Get("apiBase") = "" {
        set errorMsg = "'apiBase' not set"
        return 0
    }
    set sslConfig = config.%Get("sslConfig")
    if sslConfig '= ""{
        // Check if SSL Configuration exists
        do GetSSLConfigList^%SYS.SECURITY1(.sslConfigs)
        set key = ""
        set key = $ORDER(sslConfigs(""),1,value) 
        while (key '= ""){
            if (value = sslConfig) {
                return 1
            }
            set key = $ORDER(sslConfigs(key),1,value) 
        }
        set errorMsg = $$$FormatText($$$Text("sslConfig '%1' does not exist. Check your SSL config in the Management Portal: System Administration -> Security -> SSL/TSL Configurations", "%SQL.Function"),sslConfig)
        return 0
    }
    set checkTokenCount = config.%Get("checkTokenCount", "0")
    if (checkTokenCount){
        set maxTokens = config.%Get("maxTokens", -1)
        if (maxTokens = -1) {
            set errorMsg = "'checkTokenCount' requires that you also specify 'maxTokens'"
            return 0
        } 
    }
    return 1
}

/// Generates embeddings using Ollama embedding API endpoint
ClassMethod Embedding(input As %String, configuration As %String) As %Vector
{
    try {
        set inputData = $SELECT($ISOBJECT(input)=1:input.%ToJSON(), 1:input)
        set config = [].%FromJSON(configuration)
        set checkTokenCount = config.%Get("checkTokenCount", 0) // Defaults to false
        set modelName = config.%Get("modelName")
        set sslConfig = config.%Get("sslConfig")
        set httpConfig = config.%Get("httpConfig")
        set apiKey = config.%Get("apiKey")

        set apiBase = config.%Get("apiBase")
        do ##class(%Net.URLParser).Decompose(apiBase, .apiBaseParts)
        
        if (checkTokenCount){
            set maxTokens = config.%Get("maxTokens", -1) 
            set inputTokens = ..EstimateTokenCount(inputData)
            if (inputTokens > maxTokens){
                $$$ThrowStatus($$$ERROR($$$InputTokenExceededError, inputTokens, maxTokens))
            }
        }
    } catch e {
        $$$ThrowStatus($$$ERROR($$$EmbeddingGeneralError,"Error processing input or configuration in %Embedding.OpenAI: "_e.DisplayString()))
    }
    try{
        // Set up the HTTP request
        Set req = ##class(%Net.HttpRequest).%New()
        Set req.Server = apiBaseParts("host")
        set req.Port = apiBaseParts("port")

        if (apiKey'="") {
            Set req.Authorization = "Bearer "_apiKey
        }
        if (sslConfig'="") {
            Set req.Https = 1
            Set req.SSLConfiguration=sslConfig
        }
        Set req.ContentType = "application/json"

        // Set Http Configurations
        if (httpConfig'="") {
            set iterator = httpConfig.%GetIterator()
            while iterator.%GetNext(.key, .value) {
                set $PROPERTY(req,key) = value
            }
        }
        // Create the request body
        Set body = ##class(%Library.DynamicObject).%New()
        set body.prompt = inputData
        set body.model = modelName 
        
        // Convert the request body to JSON and write to the request
        do req.EntityBody.Write(body.%ToJSON())

        // Send POST request to the embeddings endpoint
        set endpoint = apiBaseParts("path")

    } catch e {
            $$$ThrowStatus($$$ERROR($$$EmbeddingGeneralError,"Error setting up %Net.HttpRequest: "_e.DisplayString()))
        }
    try {
        set sc = req.Post(endpoint)
        $$$ThrowOnError(sc)
        
        set statusCode = req.HttpResponse.StatusCode
        if (statusCode '= 200) {
            set response = [].%FromJSON(req.HttpResponse.Data)
            $$$ThrowStatus($$$ERROR($$$EmbeddingApiError, "openai", req.HttpResponse.StatusLine _ ". "_response.%Get("error").%Get("message")))
        }

        // Parse the JSON response
        set response = {}.%FromJSON(req.HttpResponse.Data) 
        
        // Extract the embedding data from the response
        set embeddings = response.embedding

        // Convert from dynamic array to vector
        set iter = embeddings.%GetIterator()
        while iter.%GetNext(.key,.value, .type){
            set $vector(v, $increment(i), "xf32") = value
        }
        return v

    } catch e {
        set sc = e.AsStatus()
        $$$ThrowStatus($$$ADDSC(sc, $$$ERROR($$$EmbeddingApiError,""""_apiBase_"""",e.DisplayString())))
    }
}

ClassMethod EstimateTokenCount(input As %String)
{
    set charEstimate = $NUMBER($LENGTH(input)/4,0) // 4 characters per token
    set wordEstimate = $NUMBER($LENGTH(input, " ") * 4 / 3, 0) // 3/4 words per token
    return $s(wordEstimate>charEstimate:wordEstimate, 1: charEstimate) // return larger estimate
}

}
