namespace Delivery.PEK.Models;

public record PekTown
{
    public string Name { get; init; }
    
    public IReadOnlyCollection<PekRegion> Regions { get; init; }
}