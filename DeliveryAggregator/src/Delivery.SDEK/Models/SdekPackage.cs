namespace Delivery.SDEK.Models;

public record SdekPackage
{
    public int Weight { get; init; }
    
    public int Length { get; init; }

    public int Width { get; init; }
    
    public int Height { get; init; }
}