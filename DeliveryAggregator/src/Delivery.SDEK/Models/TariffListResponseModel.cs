namespace Delivery.SDEK.Models;

public record TariffListResponseModel
{
    public TariffCodeModel[] TariffCodes { get; init; }
    
    public ErrorModel[] Errors { get; init; }
}