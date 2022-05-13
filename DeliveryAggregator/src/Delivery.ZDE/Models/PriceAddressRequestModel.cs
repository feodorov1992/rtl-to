using AutoMapper.Features;
using Newtonsoft.Json;

namespace Delivery.ZDE.Models;

public record PriceAddressRequestModel
{
    public string From { get; init; }
    
    public string To { get; init; }
    
    public int Type { get; init; }
    
    public float Weight { get; init; }
    
    public float Length { get; init; }

    public float Width { get; init; }
    
    public float Height { get; init; }
    
    public int Quantity { get; init; }
    
    public string Services { get; init; }
}