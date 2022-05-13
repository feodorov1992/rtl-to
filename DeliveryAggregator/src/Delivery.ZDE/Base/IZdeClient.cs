using Delivery.ZDE.Models;

namespace Delivery.ZDE.Base;

public interface IZdeClient
{
    Task<PriceAddressResponseModel> GetPrice(PriceAddressRequestModel request);
}