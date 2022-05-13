namespace Delivery.SDEK.Models;

public record TariffListRequestModel
{
    public SdekLocation FromLocation { get; init; }
    
    public SdekLocation ToLocation { get; init; }
    
    public SdekPackage[] Packages { get; init; }
}