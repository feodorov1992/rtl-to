namespace Delivery.PEK.Models;

public record PriceDeliveryRequestModel
{
    public float Weight { get; init; }
    
    public float Length { get; init; }

    public float Width { get; init; }
    
    public float Height { get; init; }
}