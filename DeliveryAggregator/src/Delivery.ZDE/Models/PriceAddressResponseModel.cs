namespace Delivery.ZDE.Models;

public record PriceAddressResponseModel
{
    public int Type { get; init; }

    public int Result { get; init; }

    public decimal Price { get; init; }

    public int MinDays { get; init; }

    public int MaxDays { get; init; }

    public List<PriceAddressServiceModel> Services { get; init; }
}