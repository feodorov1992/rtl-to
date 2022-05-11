using System.Runtime.Serialization;
using Microsoft.AspNetCore.Mvc.ModelBinding.Binders;
using Newtonsoft.Json;

namespace Delivery.Common.Requests;

public record DeliveryPricingRequest
{
    [JsonProperty("from_addr")]
    public string FromAddress { get; init; }
    
    [JsonProperty("to_addr")]
    public string ToAddress { get; init; }

    public float Weight { get; init; }
    
    public float Length { get; init; }
    
    public float Width { get; init; }

    public float Height { get; init; }
    
    public decimal Value { get; init; }
    
    public string Currency { get; init; }
    
    public int Quantity { get; init; }
    
    public string[] ExtraServices { get; init; }
}