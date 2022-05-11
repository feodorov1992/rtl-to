namespace Delivery.ZDE.Models;

public record PriceAddressServiceModel
{
    public string Item { get; init; }
    
    public string Price { get; init; }
    
    public string Error { get; init; }
}