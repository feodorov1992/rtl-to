using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace Delivery.PEK.Models;

public record PriceDeliveryResponseModel
{
    public object[] Take { get; init; }
    
    public object[] Delivery { get; init; }
    
    public object[] Auto { get; init; }
    
    public object[] Avia { get; init; }
    
    [JsonProperty("ADD")]
    public JObject Add { get; init; }
    
    [JsonProperty("ADD_1")]
    public JObject Add1 { get; init; }
    
    [JsonProperty("ADD_2")]
    public JObject Add2 { get; init; }
    
    [JsonProperty("ADD_3")]
    public JObject Add3 { get; init; }
    
    [JsonProperty("ADD_4")]
    public JObject Add4 { get; init; }
    
    [JsonProperty("periods_days")]
    public string PeriodsDays { get; init; }
    
    public string[] Error { get; init; }
}