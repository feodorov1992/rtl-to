namespace Delivery.SDEK.Models;

public record SdekLocation
{
    public string Address { get; init; }
    
    public string City { get; init; }
    
    public string CountryCode { get; init; }
}