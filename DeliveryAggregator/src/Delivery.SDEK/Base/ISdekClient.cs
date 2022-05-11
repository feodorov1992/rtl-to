using Delivery.SDEK.Models;

namespace Delivery.SDEK.Base;

public interface ISdekClient
{
    Task<TariffListResponseModel> GetPrices(TariffListRequestModel request);
}