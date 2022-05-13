namespace Delivery.PEK.Models;

public record GeoRegion
{
    public string Name { get; init; }
    
    public string Type { get; init; }
    
    public string Capital { get; init; }
}